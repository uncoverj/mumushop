# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb
from tgbot.database.db_item_sizes import ItemSizex


def kb_admin_sizes(position_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    sizes = ItemSizex.gets(position_id)  # position_id = это item_id


    if sizes:
        for s in sizes:
            kb.row(
                ikb(f"{s.title} — {s.qty}шт", data=f"asize:open:{position_id}:{s.increment}")
            )
    else:
        kb.row(ikb("Пока нет размеров", data="noop"))

    kb.row(
        ikb("➕ Добавить размер", data=f"asize:add:{position_id}"),
        ikb("🔙 Назад", data=f"asize:back:{position_id}"),
    )

    return kb.as_markup()


def kb_admin_size_edit(position_id: int, size_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        ikb("✏️ Переименовать", data=f"asize:rename:{position_id}:{size_id}"),
        ikb("🧮 Указать кол-во", data=f"asize:setqty:{position_id}:{size_id}"),
    ).row(
        ikb("➕ +1", data=f"asize:inc:{position_id}:{size_id}"),
        ikb("➖ -1", data=f"asize:dec:{position_id}:{size_id}"),
    ).row(
        ikb("🗑 Удалить", data=f"asize:del:{position_id}:{size_id}"),
        ikb("🔙 Назад к списку", data=f"asize:list:{position_id}"),
    )

    return kb.as_markup()
