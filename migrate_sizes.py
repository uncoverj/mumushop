import sqlite3
from tgbot.data.config import PATH_DATABASE

TABLE = "storage_item_sizes"

with sqlite3.connect(PATH_DATABASE) as con:
    cols = con.execute(f"PRAGMA table_info({TABLE})").fetchall()
    names = {c[1] for c in cols}  # name is index 1

    print("Текущие колонки:", names)

    if "position_id" not in names:
        con.execute(f"ALTER TABLE {TABLE} ADD COLUMN position_id INTEGER DEFAULT 0")
        print("✅ Добавил колонку position_id")
    else:
        print("✅ position_id уже есть")

    if "title" not in names:
        con.execute(f"ALTER TABLE {TABLE} ADD COLUMN title TEXT DEFAULT ''")
        print("✅ Добавил колонку title")

    if "qty" not in names:
        con.execute(f"ALTER TABLE {TABLE} ADD COLUMN qty INTEGER DEFAULT 0")
        print("✅ Добавил колонку qty")

print("DONE")
