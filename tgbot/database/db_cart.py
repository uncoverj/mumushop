# -*- coding: utf-8 -*-
import sqlite3
from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import ded, get_unix


class CartModel(BaseModel):
    increment: int
    user_id: int
    position_id: int
    count: int
    cart_unix: int
    # новые поля под размеры (могут быть пустыми для товаров без размеров)
    size_id: int | None = None
    size_title: str = ""


class Cartx:
    storage_name = "storage_cart"

    @staticmethod
    def create_table():
        """
        Основное создание таблицы корзины.
        На практике структура и миграции выполняются через create_dbx(),
        поэтому здесь оставляем только "страховочный" вариант с базовыми колонками.
        """
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(ded(f"""
                CREATE TABLE IF NOT EXISTS {Cartx.storage_name} (
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    cart_unix INTEGER NOT NULL,
                    size_id INTEGER,
                    size_title TEXT DEFAULT ''
                )
            """))

    @staticmethod
    def add(
        user_id: int,
        position_id: int,
        count: int = 1,
        size_id: int | None = None,
        size_title: str = "",
    ):
        cart_unix = get_unix()

        # Если в корзине уже есть такая же позиция с тем же размером —
        # просто увеличиваем количество.
        lookup_kwargs = {
            "user_id": user_id,
            "position_id": position_id,
        }
        if size_id is not None:
            lookup_kwargs["size_id"] = size_id

        existing = Cartx.get(**lookup_kwargs)
        if existing:
            return Cartx.update(existing.increment, count=int(existing.count) + int(count))

        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(ded(f"""
                INSERT INTO {Cartx.storage_name} (user_id, position_id, count, cart_unix, size_id, size_title)
                VALUES (?, ?, ?, ?, ?, ?)
            """), [user_id, position_id, int(count), cart_unix, size_id, size_title])

    @staticmethod
    def get(**kwargs) -> CartModel | None:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Cartx.storage_name}"
            sql, params = update_format_where(sql, kwargs)
            row = con.execute(sql, params).fetchone()
            return CartModel(**row) if row else None

    @staticmethod
    def gets(**kwargs) -> list[CartModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Cartx.storage_name}"
            sql, params = update_format_where(sql, kwargs)
            rows = con.execute(sql, params).fetchall()
            return [CartModel(**r) for r in rows] if rows else []

    @staticmethod
    def update(increment: int, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            sql = f"UPDATE {Cartx.storage_name} SET"
            sql, params = update_format(sql, kwargs)
            params.append(increment)
            con.execute(sql + " WHERE increment = ?", params)

    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            sql = f"DELETE FROM {Cartx.storage_name}"
            sql, params = update_format_where(sql, kwargs)
            con.execute(sql, params)

    @staticmethod
    def clear_user(user_id: int):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(f"DELETE FROM {Cartx.storage_name} WHERE user_id = ?", [user_id])
