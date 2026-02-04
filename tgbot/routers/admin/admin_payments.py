from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery

from tgbot.data.config import get_admins
from tgbot.database import Ordersx, Userx
from tgbot.utils.const_functions import ded, get_unix


router = Router(name=__name__)


@router.callback_query(F.data.startswith("pay:approve:"))
async def admin_pay_approve(call: CallbackQuery, bot: Bot):
    """
    Админ подтвердил, что оплата по заказу пришла.
    Формат callback_data: pay:approve:<order_id>:<user_id>
    """
    parts = call.data.split(":")
    if len(parts) != 4:
        return await call.answer("Некорректные данные заявки.", show_alert=True)

    _, _, order_id, user_id_str = parts

    try:
        user_id = int(user_id_str)
    except ValueError:
        return await call.answer("Некорректный ID пользователя.", show_alert=True)

    # Только администраторы из settings.ini могут подтверждать оплату
    if call.from_user.id not in get_admins():
        return await call.answer("У вас нет прав подтверждать оплату.", show_alert=True)

    order = Ordersx.get(order_id=order_id)
    if not order:
        return await call.answer("Заказ не найден в БД.", show_alert=True)

    if order.status == "paid":
        return await call.answer("Этот заказ уже помечен как оплаченный.", show_alert=True)

    # Обновляем статус заказа
    Ordersx.update(order_id, status="paid")

    # Начисляем бонусы пользователю (3% от суммы заказа)
    bonus = float(order.total_price) * 0.03
    if bonus > 0:
        Userx.add_bonus(user_id, bonus)

    # Сообщение пользователю
    await bot.send_message(
        chat_id=user_id,
        text=(
            "✅ Оплата подтверждена! Спасибо.\n"
            "Мы уже готовим ваш заказ. Администратор свяжется при необходимости."
        ),
    )

    # Обновляем сообщение в админском чате: помечаем, кто подтвердил, дату/время и убираем кнопки
    from datetime import datetime

    admin_username = f"@{call.from_user.username}" if call.from_user.username else call.from_user.full_name
    dt_text = datetime.fromtimestamp(get_unix()).strftime("%d.%m.%Y %H:%M")
    base_text = call.message.text or ""
    new_text = ded(
        f"""
        {base_text}

        ✅ ОПЛАТА ПОДТВЕРЖДЕНА админом {admin_username} {dt_text}
        """
    ).strip()

    await call.message.edit_text(new_text)
    await call.answer("Оплата отмечена как подтверждённая.", cache_time=1)


@router.callback_query(F.data.startswith("pay:reject:"))
async def admin_pay_reject(call: CallbackQuery, bot: Bot):
    """
    Админ отклоняет оплату.
    Формат callback_data: pay:reject:<order_id>:<user_id>
    """
    parts = call.data.split(":")
    if len(parts) != 4:
        return await call.answer("Некорректные данные заявки.", show_alert=True)

    _, _, order_id, user_id_str = parts

    try:
        user_id = int(user_id_str)
    except ValueError:
        return await call.answer("Некорректный ID пользователя.", show_alert=True)

    # Только администраторы
    if call.from_user.id not in get_admins():
        return await call.answer("У вас нет прав изменять оплату.", show_alert=True)

    order = Ordersx.get(order_id=order_id)
    if not order:
        return await call.answer("Заказ не найден в БД.", show_alert=True)

    if order.status == "canceled":
        return await call.answer("Заказ уже отменён.", show_alert=True)

    # Обновляем статус
    Ordersx.update(order_id, status="rejected")

    # Сообщение пользователю
    await bot.send_message(
        chat_id=user_id,
        text=(
            "❌ Оплата не подтверждена.\n"
            "Проверьте перевод и при необходимости свяжитесь с администратором."
        ),
    )

    # В группе помечаем, что оплата отклонена (кнопки убираем)
    from datetime import datetime

    admin_username = f"@{call.from_user.username}" if call.from_user.username else call.from_user.full_name
    dt_text = datetime.fromtimestamp(get_unix()).strftime("%d.%m.%Y %H:%М")
    base_text = call.message.text or ""
    new_text = ded(
        f"""
        {base_text}

        ❌ ОПЛАТА ОТКЛОНЕНА админом {admin_username} {dt_text}
        """
    ).strip()

    await call.message.edit_text(new_text)
    await call.answer("Отметка сохранена.", cache_time=1)

