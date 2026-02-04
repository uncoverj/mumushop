from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery

from tgbot.database import Ordersx
from tgbot.keyboards.reply_main import menu_frep
from tgbot.utils.const_functions import ded


router = Router(name=__name__)


@router.callback_query(F.data.startswith("order:cancel:"))
async def order_cancel(call: CallbackQuery, bot: Bot):
    """
    Пользователь отменяет уже оформленную заявку.
    callback_data: order:cancel:<order_id>
    """
    parts = call.data.split(":")
    if len(parts) != 3:
        return await call.answer("Некорректный формат заявки.", show_alert=True)

    _, _, order_id = parts
    user_id = call.from_user.id

    # Чтобы кнопка не "висела"
    await call.answer("Заявка отменена.", cache_time=1)

    order = Ordersx.get(order_id=order_id)
    if not order or int(order.user_id) != int(user_id):
        return await call.message.answer("❌ Заказ не найден или не принадлежит вам.")

    if order.status == "canceled":
        return await call.message.answer(f"Заявка #{order_id} уже отменена.", reply_markup=menu_frep(user_id))
    if order.status == "paid":
        return await call.message.answer(
            f"Заявка #{order_id} уже оплачена и не может быть отменена пользователем.",
            reply_markup=menu_frep(user_id),
        )

    # Возвращаем зарезервированные размеры по заказу (если есть size_id)
    import json
    from tgbot.database.db_item_sizes import ItemSizex

    try:
        items = json.loads(order.items_json)
    except Exception:
        items = []

    for it in items:
        size_id = it.get("size_id")
        qty = int(it.get("qty", 0) or 0)
        if not size_id or qty <= 0:
            continue
        size = ItemSizex.get(size_id)
        if not size:
            continue
        ItemSizex.set_qty(size_id, int(size.qty) + qty)

    # Обновляем статус заказа
    Ordersx.update(order_id, status="canceled")

    await call.message.answer(
        ded(
            f"""
            ✅ Заявка #{order_id} отменена.

            Если вы передумаете — можете оформить новый заказ.
            """
        ),
        reply_markup=menu_frep(user_id),
    )

