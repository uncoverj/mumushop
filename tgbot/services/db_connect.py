# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from typing import Any


def dict_factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict:
    """
    sqlite row -> dict
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def update_format(sql: str, parameters: dict) -> tuple[str, list]:
    """
    UPDATE table SET a=?, b=? ...
    """
    values = ", ".join([f"{item} = ?" for item in parameters])
    sql += f" {values}"
    return sql, list(parameters.values())


def update_format_where(sql: str, parameters: dict) -> tuple[str, list]:
    """
    ... WHERE a=? AND b=? ...
    """
    sql += " WHERE "
    sql += " AND ".join([f"{item} = ?" for item in parameters])
    return sql, list(parameters.values())
