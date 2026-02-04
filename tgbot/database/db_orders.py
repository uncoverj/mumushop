import sqlite3
from typing import Optional, List

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded


class OrderModel(BaseModel):
    increment: int
    order_id: str
    user_id: int
    status: str
    total_price: float
    items_json: str
    created_unix: int


class Ordersx:
    storage_name = "storage_orders"

    @staticmethod
    def add(
        order_id: str,
        user_id: int,
        status: str,
        total_price: float,
        items_json: str,
    ):
        created_unix = get_unix()
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(
                    f"""
                    INSERT INTO {Ordersx.storage_name} (
                        order_id,
                        user_id,
                        status,
                        total_price,
                        items_json,
                        created_unix
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """
                ),
                [order_id, int(user_id), status, float(total_price), items_json, created_unix],
            )

    @staticmethod
    def get(**kwargs) -> Optional[OrderModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Ordersx.storage_name}"
            sql, params = update_format_where(sql, kwargs)
            row = con.execute(sql, params).fetchone()
            return OrderModel(**row) if row else None

    @staticmethod
    def gets(**kwargs) -> List[OrderModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Ordersx.storage_name}"
            sql, params = update_format_where(sql, kwargs) if kwargs else (sql, [])
            rows = con.execute(sql, params).fetchall()
            return [OrderModel(**r) for r in rows] if rows else []

    @staticmethod
    def update(order_id: str, **kwargs):
        if not kwargs:
            return
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Ordersx.storage_name} SET"
            sql, params = update_format(sql, kwargs)
            params.append(order_id)
            con.execute(sql + " WHERE order_id = ?", params)

