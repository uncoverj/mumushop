# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.data.config import ORDERS_CHAT_ID
from tgbot.database import Cartx, Positionx, Itemx, Settingsx, CartSizex, Userx, Ordersx
from tgbot.database.db_item_sizes import ItemSizex
from tgbot.keyboards.inline_user_page import prod_item_category_swipe_fp
from tgbot.keyboards.reply_main import menu_frep
from tgbot.services.order_notify import tg_user_link
from tgbot.utils.const_functions import ded, del_message, gen_id, ikb
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.text_functions import open_profile_user, money

router = Router(name=__name__)


# Главное меню
@router.message(F.text == "🔙 Главное меню")
async def main_menu(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await message.answer("<b>🏠 Главное меню</b>", reply_markup=menu_frep(message.from_user.id))


################################################################################
################################# ПРОФИЛЬ ######################################
@router.message(F.text == "👤 Профиль")
async def user_profile(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await open_profile_user(bot, message.from_user.id)


################################################################################
################################# SUPPORT / FAQ ################################
@router.message(F.text == "☎️ Поддержка")
async def user_support(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    s = Settingsx.get()
    support = (s.misc_support or "None").strip()

    if support == "None" or support == "":
        return await message.answer(
            "<b>☎️ Поддержка</b>\n\n❌ Поддержка не настроена админом.",
            reply_markup=menu_frep(message.from_user.id),
        )

    if support.startswith("@"):
        support = support[1:]

    kb = InlineKeyboardBuilder()
    kb.row(ikb("💌 Написать в поддержку", url=f"https://t.me/{support}"))
    kb.row(ikb("🔙 Закрыть", data="close_this"))

    await message.answer(
        ded(f"""
            <b>☎️ Поддержка</b>
            ➖➖➖➖➖➖➖➖➖➖
            Юзернейм: <code>@{support}</code>
        """),
        reply_markup=kb.as_markup(),
    )


@router.message(F.text == "❔ FAQ")
async def user_faq(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    s = Settingsx.get()
    faq_text = (s.misc_faq or "None").strip()

    if faq_text == "None" or faq_text == "":
        faq_text = "❌ FAQ пока не заполнен админом."

    kb = InlineKeyboardBuilder()
    kb.row(ikb("🔙 Закрыть", data="close_this"))

    await message.answer(
        ded(f"""
            <b>❔ FAQ</b>
            ➖➖➖➖➖➖➖➖➖➖
            {faq_text}
        """),
        reply_markup=kb.as_markup(),
    )


################################################################################
################################# КОРЗИНА ######################################
def _cart_kb(user_id: int, rows: list):
    kb = InlineKeyboardBuilder()

    for row in rows[:20]:
        inc = row[0]
        name = row[3]
        cnt = row[2]
        price_one = row[4]
        kb.row(
            ikb(f"❌ {name} x{cnt} ({money(price_one)})", data=f"cart_remove:{inc}"),
        )

    kb.row(
        ikb("🧹 Очистить корзину", data="cart_clear"),
        ikb("✅ Оформить заявку", data="cart_checkout"),
    )
    kb.row(ikb("🔄 Обновить", data="cart_open"))
    kb.row(ikb("🔙 Закрыть", data="close_this"))

    return kb.as_markup()


async def _render_cart_text(user_id: int) -> tuple[str, list]:
    cart_rows = Cartx.gets(user_id=user_id)

    if not cart_rows:
        return "<b>🧺 Корзина пуста</b>\n\nВыберите товар и нажмите «🛒 В корзину».", []

    lines = []
    total = 0
    rows = []

    for c in cart_rows:
        pos = Positionx.get(position_id=c.position_id)
        if not pos:
            Cartx.delete(increment=c.increment)
            continue

        sum_pos = (pos.position_price or 0) * c.count
        total += sum_pos

        rows.append((c.increment, c.position_id, c.count, pos.position_name, pos.position_price, sum_pos))

        # Если у товара выбран размер — добавим его в строку
        size_part = ""
        if getattr(c, "size_title", ""):
            size_part = f" ({c.size_title} x{c.count})"

        lines.append(
            f"• <code>{pos.position_name}</code> — {c.count} шт{size_part} × {money(pos.position_price)} = <b>{money(sum_pos)}</b>"
        )

    text = ded(f"""
        <b>🧺 Ваша корзина</b>
        ➖➖➖➖➖➖➖➖➖➖
        {chr(10).join(lines)}

        ➖➖➖➖➖➖➖➖➖➖
        <b>Итого:</b> <code>{money(total)}</code>

        <i>Оплата в боте отключена — админ свяжется с вами.</i>
    """)

    return text, rows


def _restore_sizes_for_user(user_id: int, position_id: int | None = None):
    """
    Возвращает зарезервированные размеры в остатки для корзины пользователя.
    Используется при очистке/удалении из корзины ДО оформления заказа.
    """
    from tgbot.database.db_item_sizes import ItemSizex  # локальный импорт, чтобы избежать циклов

    cart_rows = Cartx.gets(user_id=user_id)
    if not cart_rows:
        return

    for c in cart_rows:
        if position_id is not None and c.position_id != position_id:
            continue
        size_id = getattr(c, "size_id", None)
        if size_id is None:
            continue
        size = ItemSizex.get(size_id)
        if not size:
            continue
        ItemSizex.set_qty(size_id, int(size.qty) + int(c.count))


@router.message(F.text == "🧺 Корзина")
async def cart_open_from_menu(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    text, rows = await _render_cart_text(message.from_user.id)
    await message.answer(text, reply_markup=_cart_kb(message.from_user.id, rows))


@router.callback_query(F.data == "cart_open")
async def cart_open_inline(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    text, rows = await _render_cart_text(call.from_user.id)
    await call.message.edit_text(text, reply_markup=_cart_kb(call.from_user.id, rows))


@router.callback_query(F.data == "cart_clear")
async def cart_clear(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = call.from_user.id
    # Вернём все зарезервированные размеры в остатки
    _restore_sizes_for_user(user_id)
    Cartx.clear_user(user_id)
    CartSizex.clear_user(user_id)
    text, rows = await _render_cart_text(call.from_user.id)
    await call.message.edit_text(text, reply_markup=_cart_kb(call.from_user.id, rows))


@router.callback_query(F.data.startswith("cart_remove:"))
async def cart_remove_one(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    inc = int(call.data.split(":")[1])

    # узнаём позицию перед удалением, чтобы удалить её размеры
    cart_row = Cartx.get(increment=inc)
    if cart_row:
        # Вернём размеры по этой позиции
        _restore_sizes_for_user(call.from_user.id, cart_row.position_id)
        CartSizex.delete_for_position(user_id=call.from_user.id, position_id=cart_row.position_id)

    Cartx.delete(increment=inc)
    text, rows = await _render_cart_text(call.from_user.id)
    await call.message.edit_text(text, reply_markup=_cart_kb(call.from_user.id, rows))


@router.callback_query(F.data == "cart_checkout")
async def cart_checkout(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = call.from_user.id
    cart_rows = Cartx.gets(user_id=user_id)

    if not cart_rows:
        return await call.answer("Корзина пуста", True)

    items_text = []
    total = 0

    for c in cart_rows:
        pos = Positionx.get(position_id=c.position_id)
        if not pos:
            continue

        # Позиции без размеров: проверка по Itemx (как раньше)
        size_defs = ItemSizex.gets(position_id=c.position_id)
        if not size_defs:
            available = len(Itemx.gets(position_id=c.position_id))
            if c.count > available:
                text, rows = await _render_cart_text(user_id)
                return await call.message.edit_text(
                    ded(f"""
                        <b>❌ Недостаточно товара</b>
                        ▪️ Товар: <code>{pos.position_name}</code>
                        ▪️ В корзине: <code>{c.count}шт</code>
                        ▪️ В наличии: <code>{available}шт</code>

                        <i>Уменьши количество или удали товар из корзины.</i>
                    """),
                    reply_markup=_cart_kb(user_id, rows),
                )

        s = (pos.position_price or 0) * c.count
        total += s

        # Формируем текст с учётом выбранного размера (если есть)
        size_part = ""
        if getattr(c, "size_title", ""):
            size_part = f" ({c.size_title} x{c.count})"
        items_text.append(f"• {pos.position_name} — {c.count}шт{size_part} = {money(s)}")

    # Учитываем бонусы пользователя (если есть)
    user = Userx.get(user_id=user_id)
    user_bonus = user.user_balance if user else 0
    bonus_used = min(user_bonus, total)
    total_to_pay = total - bonus_used

    # Формируем текст заказа для пользователя
    items_block = chr(10).join(items_text)
    pay_text = ded(f"""
        <b>🧺 Ваш заказ</b>
        ➖➖➖➖➖➖➖➖➖➖
        {items_block}

        <b>Сумма заказа:</b> <code>{money(total)}</code>
        <b>Бонусы:</b> <code>-{money(bonus_used)}</code>
        <b>Итого к оплате:</b> <code>{money(total_to_pay)}</code>

        <b>💳 Оплата по карте</b>
        ▪️ Номер карты: <code>5440 8100 0891 1330</code>
        ▪️ Владелец: <code>MUHAMEDGARAEV AMAL</code>

        <i>После оплаты нажмите «✅ Оплатил» или отмените заявку.</i>
    """)

    kb = InlineKeyboardBuilder()
    kb.row(
        ikb("✅ Оплатил", data="cart_pay_confirm"),
        ikb("❌ Отменить", data="cart_pay_cancel"),
    )
    kb.row(ikb("🔙 В корзину", data="cart_open"))

    await call.message.edit_text(pay_text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "cart_pay_cancel")
async def cart_pay_cancel(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    """Пользователь отменяет оформление после показа реквизитов."""
    user_id = call.from_user.id
    # Вернём все зарезервированные размеры и очистим корзину
    _restore_sizes_for_user(user_id)
    Cartx.clear_user(user_id)
    CartSizex.clear_user(user_id)

    await call.message.edit_text(
        "<b>❌ Заявка отменена.</b>\n\n"
        "Корзина очищена, заказ админам не отправлен.\n"
        "Вы можете выбрать товары и оформить новый заказ.",
        reply_markup=menu_frep(user_id),
    )


@router.callback_query(F.data == "cart_pay_confirm")
async def cart_pay_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    """Пользователь нажал «Оплатил» после перевода на карту."""
    user_id = call.from_user.id
    cart_rows = Cartx.gets(user_id=user_id)

    if not cart_rows:
        return await call.answer("Корзина пуста или уже оформлена.", True)

    items_text = []
    total = 0

    # Сначала проверяем остатки по размерам и без размеров.
    # Для позиций с размерами: проверяем остаток по каждому конкретному размеру.
    from tgbot.database.db_item_sizes import ItemSizex  # локальный импорт

    for c in cart_rows:
        pos = Positionx.get(position_id=c.position_id)
        if not pos:
            continue

        if getattr(c, "size_id", None) is not None:
            size = ItemSizex.get(c.size_id)
            if not size or size.qty < c.count:
                text, rows = await _render_cart_text(user_id)
                size_title = getattr(c, "size_title", "") or "неизвестный"
                return await call.message.edit_text(
                    ded(f"""
                        <b>❌ Недостаточно товара по размеру {size_title}</b>
                        ▪️ Товар: <code>{pos.position_name}</code>
                        ▪️ В корзине: <code>{c.count}шт</code>
                        ▪️ В наличии: <code>{size.qty if size else 0}шт</code>

                        <i>Уменьши количество или выбери другой размер.</i>
                    """),
                    reply_markup=_cart_kb(user_id, rows),
                )
        else:
            # Старый режим без размеров: проверяем наличие по Itemx
            available = len(Itemx.gets(position_id=c.position_id))
            if c.count > available:
                text, rows = await _render_cart_text(user_id)
                return await call.message.edit_text(
                    ded(f"""
                        <b>❌ Недостаточно товара</b>
                        ▪️ Товар: <code>{pos.position_name}</code>
                        ▪️ В корзине: <code>{c.count}шт</code>
                        ▪️ В наличии: <code>{available}шт</code>

                        <i>Уменьши количество или удали товар из корзины.</i>
                    """),
                    reply_markup=_cart_kb(user_id, rows),
                )

    # Если все проверки пройдены — считаем суммы и параллельно подготавливаем текст
    total = 0
    for c in cart_rows:
        pos = Positionx.get(position_id=c.position_id)
        if not pos:
            continue

        s = (pos.position_price or 0) * c.count
        total += s

        size_part = ""
        if getattr(c, "size_title", ""):
            size_part = f" ({c.size_title} x{c.count})"
        items_text.append(f"• {pos.position_name} — {c.count}шт{size_part} = {money(s)}")

    # Учитываем бонусы пользователя (если есть) — окончательная сумма к оплате
    user = Userx.get(user_id=user_id)
    user_bonus = user.user_balance if user else 0
    bonus_used = min(user_bonus, total)
    total_to_pay = total - bonus_used

    order_id = str(gen_id(10))
    total_count = sum(c.count for c in cart_rows)
    link = tg_user_link(user_id, call.from_user.username)

    # Сохраняем заказ в БД (items_json: позиции + qty + size_id)
    import json as _json

    items_payload = []
    for c in cart_rows:
        items_payload.append(
            {
                "position_id": c.position_id,
                "qty": int(c.count),
                "size_id": getattr(c, "size_id", None),
            }
        )

    Ordersx.add(
        order_id=order_id,
        user_id=user_id,
        status="pending",
        total_price=float(total_to_pay),
        items_json=_json.dumps(items_payload, ensure_ascii=False),
    )

    if ORDERS_CHAT_ID != 0:
        text_admin = ded(f"""
            🧺 НОВЫЙ ЗАКАЗ (оплата переводом на карту)
            🆔 Заявка: #{order_id}
            👤 Клиент: {call.from_user.first_name or '-'} (@{call.from_user.username or 'нет'})
            🧾 TG ID: {user_id}
            🔗 Написать: {link}

            📦 Состав заказа:
            {chr(10).join(items_text)}

            💰 Сумма заказа: {money(total)}
            🎁 Бонусы клиента: {money(bonus_used)}
            💳 К оплате: {money(total_to_pay)}

            💳 Оплата: перевод на карту 5440 8100 0891 1330 (MUHAMEDGARAEV AMAL)
        """)
        from aiogram.utils.keyboard import InlineKeyboardBuilder as _AdminKB  # локальный алиас, чтобы не путаться
        admin_kb = _AdminKB()
        admin_kb.row(
            ikb(
                "✅ Подтвердить оплату",
                data=f"pay:approve:{order_id}:{user_id}",
            ),
            ikb(
                "❌ Отклонить оплату",
                data=f"pay:reject:{order_id}:{user_id}",
            ),
        )
        try:
            # В этот чат (группа/канал/ЛС) уходят заявки для админов
            await bot.send_message(ORDERS_CHAT_ID, text_admin, reply_markup=admin_kb.as_markup())
        except Exception as e:
            return await call.message.edit_text(
                "<b>❌ Не удалось отправить заявку админам</b>\n"
                f"<code>{e}</code>\n\n"
                "<i>Проверь: orders_chat_id, бот в группе, права на сообщения.</i>"
            )

    Cartx.clear_user(user_id)
    CartSizex.clear_user(user_id)

    await del_message(call.message)
    await call.message.answer(
        ded(f"""
            <b>✅ Заявка отправлена админам!</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Номер заявки: <code>#{order_id}</code>
            ▪️ Итого: <code>{money(total)}</code>

            <i>Ожидайте: после проверки оплаты админ подтвердит заказ.</i>
        """),
        reply_markup=menu_frep(user_id),
    )


################################################################################
################################# ПОКУПКИ ######################################
@router.message(F.text == "🧮 Наличие товаров")

async def user_buy(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await message.answer(
        "<b>🎁 Выберите нужный вам товар</b>",
        reply_markup=prod_item_category_swipe_fp(0),
    )


################################################################################
################################# CLOSE ########################################
@router.callback_query(F.data == "close_this")
async def close_this(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await del_message(call.message)
