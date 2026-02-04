from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_item_sizes import ItemSizex

def kb_sizes_for_item(item_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    sizes = ItemSizex.gets(item_id)
    sizes = [s for s in sizes if s.qty > 0]

    for s in sizes:
        # ВАЖНО: item_id + size_id
        b.button(text=f"{s.title} ({s.qty})", callback_data=f"size:pick:{item_id}:{s.size_id}")

    b.adjust(3)
    b.button(text="⬅️ Назад", callback_data=f"item:back:{item_id}")
    b.adjust(3, 1)
    return b.as_markup()
