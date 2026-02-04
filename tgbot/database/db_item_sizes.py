# -*- coding: utf-8 -*-

import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Set

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import ded, get_unix

print("USING db_item_sizes FROM:", __file__)


def dict_factory(cursor, row) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@dataclass
class ItemSizeModel:
    # ЕДИНЫЙ формат модели, независимо от схемы БД
    size_id: int
    item_id: int
    title: str
    qty: int
    created_unix: int = 0  # по умолчанию, если в старой схеме нет created_unix

    # ✅ совместимость со старым кодом (inline_admin_sizes использует increment)
    @property
    def increment(self) -> int:
        return self.size_id

    # ✅ совместимость со старым кодом (admin_sizes / другие места используют position_id)
    @property
    def position_id(self) -> int:
        return self.item_id


class ItemSizex:
    storage_name = "storage_item_sizes"

    @staticmethod
    def create_table():
        """
        Создаём таблицу в новом формате (как в db_helper.py).
        Если у тебя старая таблица — код ниже умеет работать и с ней, без удаления данных.
        """
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(ded(f"""
                CREATE TABLE IF NOT EXISTS {ItemSizex.storage_name} (
                    size_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    qty INTEGER NOT NULL DEFAULT 0,
                    created_unix INTEGER NOT NULL
                )
            """))
            con.execute(
                f"CREATE INDEX IF NOT EXISTS idx_sizes_item ON {ItemSizex.storage_name}(item_id)"
            )

    @staticmethod
    def _cols(con) -> Set[str]:
        """
        Возвращает set имен колонок таблицы.
        PRAGMA может вернуть list[tuple] или list[dict] — обрабатываем оба варианта.
        """
        rows = con.execute(f"PRAGMA table_info({ItemSizex.storage_name})").fetchall()
        if not rows:
            return set()

        first = rows[0]
        # dict-вариант (если где-то включили row_factory)
        if isinstance(first, dict):
            return {r.get("name") for r in rows if r.get("name")}
        # tuple-вариант: (cid, name, type, notnull, dflt_value, pk)
        return {r[1] for r in rows if isinstance(r, (tuple, list)) and len(r) > 1}

    @staticmethod
    def _schema(con) -> Dict[str, Any]:
        """
        Определяем реальную схему таблицы.
        Новая: size_id + item_id (+ created_unix)
        Старая: increment + position_id (created_unix может отсутствовать)
        """
        cols = ItemSizex._cols(con)

        if "size_id" in cols and "item_id" in cols:
            return {
                "pk": "size_id",
                "item": "item_id",
                "has_created": "created_unix" in cols,
                "cols": cols,
            }

        # fallback на старую схему
        return {
            "pk": "increment",
            "item": "position_id",
            "has_created": "created_unix" in cols,
            "cols": cols,
        }

    @staticmethod
    def add(*, position_id: Optional[int] = None, item_id: Optional[int] = None, title: str, qty: int):
        """
        Совместимость:
        - старый код вызывает: add(position_id=..., title=..., qty=...)
        - новый код может вызывать: add(item_id=..., title=..., qty=...)
        """
        pid = item_id if item_id is not None else position_id
        if pid is None:
            raise ValueError("ItemSizex.add: нужно передать position_id или item_id")

        with sqlite3.connect(PATH_DATABASE) as con:
            schema = ItemSizex._schema(con)
            cols = schema["cols"]

            fields = [schema["item"], "title", "qty"]
            values = [int(pid), str(title), int(qty)]

            if schema["has_created"] and "created_unix" in cols:
                fields.append("created_unix")
                values.append(int(get_unix()))

            placeholders = ", ".join(["?"] * len(fields))
            con.execute(
                f"INSERT INTO {ItemSizex.storage_name} ({', '.join(fields)}) VALUES ({placeholders})",
                values,
            )

    @staticmethod
    def gets(position_id: int) -> List[ItemSizeModel]:
        """
        position_id — оставляем старое имя параметра, но внутри мапим как item_id.
        """
        with sqlite3.connect(PATH_DATABASE) as con:
            schema = ItemSizex._schema(con)
            pk = schema["pk"]
            item = schema["item"]
            created = "created_unix" if schema["has_created"] else "0 AS created_unix"

            con.row_factory = dict_factory
            rows = con.execute(
                f"""
                SELECT
                    {pk} AS size_id,
                    {item} AS item_id,
                    title,
                    qty,
                    {created}
                FROM {ItemSizex.storage_name}
                WHERE {item} = ?
                ORDER BY {pk} DESC
                """,
                (int(position_id),),
            ).fetchall()

            return [ItemSizeModel(**r) for r in rows] if rows else []

    @staticmethod
    def get(size_id: int) -> Optional[ItemSizeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            schema = ItemSizex._schema(con)
            pk = schema["pk"]
            item = schema["item"]
            created = "created_unix" if schema["has_created"] else "0 AS created_unix"

            con.row_factory = dict_factory
            row = con.execute(
                f"""
                SELECT
                    {pk} AS size_id,
                    {item} AS item_id,
                    title,
                    qty,
                    {created}
                FROM {ItemSizex.storage_name}
                WHERE {pk} = ?
                """,
                (int(size_id),),
            ).fetchone()

            return ItemSizeModel(**row) if row else None

    @staticmethod
    def update(size_id: int, **kwargs):
        if not kwargs:
            return

        with sqlite3.connect(PATH_DATABASE) as con:
            schema = ItemSizex._schema(con)
            pk = schema["pk"]
            cols = schema["cols"]

            # обновляем только реальные колонки таблицы
            safe = {k: v for k, v in kwargs.items() if k in cols}
            if not safe:
                return

            keys = ", ".join([f"{k} = ?" for k in safe.keys()])
            values = list(safe.values()) + [int(size_id)]

            con.execute(
                f"UPDATE {ItemSizex.storage_name} SET {keys} WHERE {pk} = ?",
                values,
            )

    @staticmethod
    def set_qty(size_id: int, qty: int):
        ItemSizex.update(size_id, qty=int(qty))

    @staticmethod
    def delete(size_id: int):
        with sqlite3.connect(PATH_DATABASE) as con:
            schema = ItemSizex._schema(con)
            pk = schema["pk"]
            con.execute(
                f"DELETE FROM {ItemSizex.storage_name} WHERE {pk} = ?",
                (int(size_id),),
            )
