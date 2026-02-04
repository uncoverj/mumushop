# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tgbot.data.config import get_admins
from tgbot.utils.const_functions import rkb


# Главное меню
def menu_frep(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    # Пользовательские кнопки
    kb.row(
        rkb("🧮 Наличие товаров"),  # вместо "Купить"
        rkb("🧺 Корзина"),
        rkb("👤 Профиль"),
    ).row(
        rkb("☎️ Поддержка"),
        rkb("❔ FAQ"),
    )

    # Админские кнопки
    if user_id in get_admins():
        kb.row(
            rkb("🎁 Управление товарами"),
            rkb("📊 Статистика"),
        ).row(
            rkb("⚙️ Настройки"),
            rkb("🔆 Общие функции"),
        )

    return kb.as_markup(resize_keyboard=True)


# Общие функции (админ)
def functions_frep() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        rkb("🔍 Поиск"),
        rkb("📢 Рассылка"),
    ).row(
        rkb("🔙 Главное меню"),
    )
    return kb.as_markup(resize_keyboard=True)


# Настройки (админ)
def settings_frep() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        rkb("🖍 Изменить данные"),
        rkb("🕹 Выключатели"),
    ).row(
        rkb("🔙 Главное меню"),
    )
    return kb.as_markup(resize_keyboard=True)


# Управление товарами (админ)
def items_frep() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        rkb("📁 Создать позицию ➕"),
        rkb("🗃 Создать категорию ➕"),
    ).row(
        rkb("📁 Изменить позицию 🖍"),
        rkb("🗃 Изменить категорию 🖍"),
    ).row(
        rkb("❌ Удаление"),
    ).row(
        rkb("🔙 Главное меню"),
    )
    return kb.as_markup(resize_keyboard=True)
