# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb
from tgbot.database.db_item_sizes import ItemSizex


# Клавиатура на карточке товара
def products_open_finl(position_id: int, category_id: int, remover: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # Проверяем, есть ли размеры с остатком для этой позиции
    sizes = ItemSizex.gets(position_id)
    sizes = [s for s in sizes if s.qty > 0]

    if sizes:
        # Если есть размеры — сначала предлагаем выбрать размер
        kb.row(
            ikb("📏 Выбрать размер", data=f"size:open:{position_id}"),
        )
    else:
        # Если размеров нет — обычная кнопка в корзину
        kb.row(
            ikb("🛒 В корзину", data=f"cart_add:{position_id}:1"),
        )

    kb.row(
        ikb("🔙 Назад", data=f"buy_position_swipe:{category_id}:{remover}"),
    )

    return kb.as_markup()


# Если где-то в коде ещё импортируются старые функции — оставляем заглушки,
# чтобы бот не падал на ImportError.
def products_buy_confirm_finl(*args, **kwargs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(ikb("🔙 Назад", data="close_this"))
    return kb.as_markup()

def products_return_finl(*args, **kwargs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(ikb("🔙 Назад", data="close_this"))
    return kb.as_markup()

def cart_confirm_finl(*args, **kwargs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(ikb("🔙 Назад", data="close_this"))
    return kb.as_markup()

def cart_item_manage_finl(*args, **kwargs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(ikb("🔙 Назад", data="close_this"))
    return kb.as_markup()
