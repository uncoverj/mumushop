# -*- coding: utf-8 -*-
import configparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_CONFIG = configparser.ConfigParser()
BOT_CONFIG.read("settings.ini", encoding="utf-8")

# ===== Основные настройки =====
BOT_TOKEN = BOT_CONFIG["settings"].get("bot_token", "").strip()

# Discord webhook (если не нужен — можно оставить пустым в settings.ini)
DISCORD_WEBHOOK = BOT_CONFIG["settings"].get("discord_webhook", "").strip()

# TG чат/группа/канал куда будут падать заказы (без оплаты)
# если нет в settings.ini — будет 0 и бот не упадёт
ORDERS_CHAT_ID = int(BOT_CONFIG["settings"].get("orders_chat_id", "0"))

# ✅ Валюта (узбекский сум)
CURRENCY = "сум"   # можно "UZS" если хочешь

BOT_TIMEZONE = BOT_CONFIG["settings"].get("bot_timezone", "Asia/Tashkent").strip()
BOT_SCHEDULER = AsyncIOScheduler(timezone=BOT_TIMEZONE)
BOT_VERSION = 4.1
CURRENCY_SYMBOL = "сум"
# ===== Валюта =====
CURRENCY_SYMBOL = BOT_CONFIG["settings"].get("currency_symbol", "сум").strip() or "сум"


# ===== Пути =====
PATH_DATABASE = "tgbot/data/database.db"
PATH_LOGS = "tgbot/data/logs.log"


# ===== Администраторы =====
def get_admins() -> list[int]:
    admins_raw = BOT_CONFIG["settings"].get("admin_id", "").replace(" ", "")
    if not admins_raw:
        return []

    admins = admins_raw.split(",")
    clean = []
    for a in admins:
        a = a.strip()
        if a.isdigit():
            clean.append(int(a))
    return clean


# ===== Описание бота =====
def get_desc() -> str:
    return "👑 Разработчик: t.me/Uncoverj"
