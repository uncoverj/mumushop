import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory
from tgbot.utils.const_functions import get_unix, ded


@dataclass
class CartSizeModel:
    increment: int
    user_id: int
    position_id: int
    size_id: int
    size_title: str
    cart_unix: int


class CartSizex:
    storage_name = "storage_cart_sizes"

    @staticmethod
    def create_table():
        """
        Создание таблицы для хранения выбранных размеров в корзине.
        Один ряд = одна единица товара определённого размера.
        """
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                ded(
                    f"""
                    CREATE TABLE IF NOT EXISTS {CartSizex.storage_name} (
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        position_id INTEGER NOT NULL,
                        size_id INTEGER NOT NULL,
                        size_title TEXT NOT NULL,
                        cart_unix INTEGER NOT NULL
                    )
                    """
                )
            )

    @staticmethod
    def add(user_id: int, position_id: int, size_id: int, size_title: str):
        cart_unix = get_unix()
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                ded(
                    f"""
                    INSERT INTO {CartSizex.storage_name}
                        (user_id, position_id, size_id, size_title, cart_unix)
                    VALUES (?, ?, ?, ?, ?)
                    """
                ),
                [int(user_id), int(position_id), int(size_id), str(size_title), cart_unix],
            )

    @staticmethod
    def gets(user_id: Optional[int] = None, position_id: Optional[int] = None) -> List[CartSizeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {CartSizex.storage_name}"
            params = []
            conds = []

            if user_id is not None:
                conds.append("user_id = ?")
                params.append(int(user_id))
            if position_id is not None:
                conds.append("position_id = ?")
                params.append(int(position_id))

            if conds:
                sql += " WHERE " + " AND ".join(conds)

            rows = con.execute(sql, params).fetchall()
            return [CartSizeModel(**r) for r in rows] if rows else []

    @staticmethod
    def clear_user(user_id: int):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                f"DELETE FROM {CartSizex.storage_name} WHERE user_id = ?",
                [int(user_id)],
            )

    @staticmethod
    def delete_for_position(user_id: int, position_id: int):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                f"DELETE FROM {CartSizex.storage_name} WHERE user_id = ? AND position_id = ?",
                [int(user_id), int(position_id)],
            )

