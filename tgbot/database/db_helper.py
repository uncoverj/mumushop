# - *- coding: utf- 8 - *-
import sqlite3

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import get_unix, ded


def dict_factory(cursor, row) -> dict:
    save_dict = {}
    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]
    return save_dict


def update_format(sql, parameters: dict) -> tuple[str, list]:
    values = ", ".join([f"{item} = ?" for item in parameters])
    sql += f" {values}"
    return sql, list(parameters.values())


def update_format_where(sql, parameters: dict) -> tuple[str, list]:
    sql += " WHERE "
    sql += " AND ".join([f"{item} = ?" for item in parameters])
    return sql, list(parameters.values())


################################################################################
# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        ############################################################
        # storage_users
        if len(con.execute("PRAGMA table_info(storage_users)").fetchall()) == 8:
            print("DB was found(1/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_users(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_login TEXT,
                    user_name TEXT,
                    user_balance REAL,
                    user_refill REAL,
                    user_give REAL,
                    user_unix INTEGER
                )
            """))
            print("DB was not found(1/9) | Creating...")

        ############################################################
        # storage_settings
        if len(con.execute("PRAGMA table_info(storage_settings)").fetchall()) == 13:
            print("DB was found(2/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_settings(
                    status_work TEXT,
                    status_refill TEXT,
                    status_buy TEXT,
                    misc_faq TEXT,
                    misc_support TEXT,
                    misc_bot TEXT,
                    misc_discord_webhook_url TEXT,
                    misc_discord_webhook_name TEXT,
                    misc_hide_category TEXT,
                    misc_hide_position TEXT,
                    misc_profit_day INTEGER,
                    misc_profit_week INTEGER,
                    misc_profit_month INTEGER
                )
            """))

            con.execute(ded("""
                INSERT INTO storage_settings(
                    status_work,
                    status_refill,
                    status_buy,
                    misc_faq,
                    misc_support,
                    misc_bot,
                    misc_discord_webhook_url,
                    misc_discord_webhook_name,
                    misc_hide_category,
                    misc_hide_position,
                    misc_profit_day,
                    misc_profit_week,
                    misc_profit_month
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), [
                "True", "False", "False",
                "None", "None", "None",
                "None", "None",
                "False", "False",
                get_unix(), get_unix(), get_unix()
            ])
            print("DB was not found(2/9) | Creating...")

        ############################################################
        # storage_payments
        if len(con.execute("PRAGMA table_info(storage_payments)").fetchall()) == 4:
            print("DB was found(3/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_payments(
                    cryptobot_token TEXT,
                    yoomoney_token TEXT,
                    status_cryptobot TEXT,
                    status_yoomoney TEXT
                )
            """))

            con.execute(ded("""
                INSERT INTO storage_payments(
                    cryptobot_token,
                    yoomoney_token,
                    status_cryptobot,
                    status_yoomoney
                )
                VALUES (?, ?, ?, ?)
            """), ["None", "None", "False", "False"])
            print("DB was not found(3/9) | Creating...")

        ############################################################
        # storage_refill
        if len(con.execute("PRAGMA table_info(storage_refill)").fetchall()) == 7:
            print("DB was found(4/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_refill(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    refill_comment TEXT,
                    refill_amount REAL,
                    refill_receipt TEXT,
                    refill_method TEXT,
                    refill_unix INTEGER
                )
            """))
            print("DB was not found(4/9) | Creating...")

        ############################################################
        # storage_category
        if len(con.execute("PRAGMA table_info(storage_category)").fetchall()) == 4:
            print("DB was found(5/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_category(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    category_name TEXT,
                    category_unix INTEGER
                )
            """))
            print("DB was not found(5/9) | Creating...")

        ############################################################
        # storage_position
        if len(con.execute("PRAGMA table_info(storage_position)").fetchall()) == 8:
            print("DB was found(6/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_position(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    position_id INTEGER,
                    position_name TEXT,
                    position_price REAL,
                    position_desc TEXT,
                    position_photo TEXT,
                    position_unix INTEGER
                )
            """))
            print("DB was not found(6/9) | Creating...")

        ############################################################
        # storage_item
        if len(con.execute("PRAGMA table_info(storage_item)").fetchall()) == 7:
            print("DB was found(7/9)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_item(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_id INTEGER,
                    position_id INTEGER,
                    item_id INTEGER,
                    item_unix INTEGER,
                    item_data TEXT
                )
            """))
            print("DB was not found(7/9) | Creating...")

        ############################################################
        # storage_purchases
        if len(con.execute("PRAGMA table_info(storage_purchases)").fetchall()) == 14:
            print("DB was found(8/10)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_purchases(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_balance_before REAL,
                    user_balance_after REAL,
                    purchase_receipt TEXT,
                    purchase_data TEXT,
                    purchase_count INTEGER,
                    purchase_price REAL,
                    purchase_price_one REAL,
                    purchase_position_id INTEGER,
                    purchase_position_name TEXT,
                    purchase_category_id INTEGER,
                    purchase_category_name TEXT,
                    purchase_unix INTEGER
                )
            """))
            print("DB was not found(8/10) | Creating...")

        ############################################################
        # storage_orders
        if len(con.execute("PRAGMA table_info(storage_orders)").fetchall()) == 7:
            print("DB was found(9/10)")
        else:
            con.execute(ded("""
                CREATE TABLE storage_orders(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE,
                    user_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    items_json TEXT NOT NULL,
                    created_unix INTEGER NOT NULL
                )
            """))
            print("DB was not found(9/10) | Creating storage_orders...")

        ############################################################
        # storage_cart (+ миграции со старых структур)
        # Итоговая целевая схема:
        # increment | user_id | position_id | position_name | price_one | count | cart_unix | size_id | size_title
        cart_cols = con.execute("PRAGMA table_info(storage_cart)").fetchall()

        if not cart_cols:
            # создаём таблицу сразу в новом формате
            con.execute(ded("""
                CREATE TABLE storage_cart(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    position_id INTEGER,
                    position_name TEXT,
                    price_one REAL,
                    count INTEGER,
                    cart_unix INTEGER,
                    size_id INTEGER,
                    size_title TEXT
                )
            """))
            print("DB was not found(9/9) | Creating storage_cart (with sizes)...")
        else:
            # есть таблица, мигрируем по именам колонок (а не по количеству)
            try:
                existing_names = {c["name"] for c in cart_cols}
            except Exception:
                # на всякий случай, если row_factory вдруг не dict_factory
                existing_names = {c[1] for c in cart_cols if len(c) > 1}

            print(f"DB was found(9/9) | storage_cart cols={len(cart_cols)} -> {sorted(existing_names)}")

            # со старой 5-колоночной структуры добавляем недостающие поля позиции/цены
            if "position_name" not in existing_names:
                con.execute("ALTER TABLE storage_cart ADD COLUMN position_name TEXT DEFAULT ''")
                print("MIGRATION: add column storage_cart.position_name")
            if "price_one" not in existing_names:
                con.execute("ALTER TABLE storage_cart ADD COLUMN price_one REAL DEFAULT 0")
                print("MIGRATION: add column storage_cart.price_one")

            # новые поля под размеры
            if "size_id" not in existing_names:
                con.execute("ALTER TABLE storage_cart ADD COLUMN size_id INTEGER DEFAULT NULL")
                print("MIGRATION: add column storage_cart.size_id")
            if "size_title" not in existing_names:
                con.execute("ALTER TABLE storage_cart ADD COLUMN size_title TEXT DEFAULT ''")
                print("MIGRATION: add column storage_cart.size_title")
        ############################################################
        # storage_item_sizes (размеры товара)
        # size_id | item_id | title | qty | created_unix
        sizes_cols = con.execute("PRAGMA table_info(storage_item_sizes)").fetchall()

        if not sizes_cols:
            con.execute(ded("""
                CREATE TABLE storage_item_sizes(
                    size_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    qty INTEGER NOT NULL DEFAULT 0,
                    created_unix INTEGER NOT NULL
                )
            """))
            con.execute("CREATE INDEX IF NOT EXISTS idx_sizes_item ON storage_item_sizes(item_id)")
            print("DB was not found(10/10) | Creating storage_item_sizes...")
        else:
            print("DB was found(10/10)")

        ############################################################
        # storage_cart_sizes (связка корзины и размеров)
        cart_sizes_cols = con.execute("PRAGMA table_info(storage_cart_sizes)").fetchall()
        if not cart_sizes_cols:
            con.execute(ded("""
                CREATE TABLE storage_cart_sizes(
                    increment INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    size_id INTEGER NOT NULL,
                    size_title TEXT NOT NULL,
                    cart_unix INTEGER NOT NULL
                )
            """))
            print("DB extra: creating storage_cart_sizes...")
        else:
            print("DB extra: storage_cart_sizes found")
