# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database import Purchasesx, Refillx, Userx
from tgbot.keyboards.inline_admin import profile_edit_return_finl, mail_confirm_finl
from tgbot.utils.const_functions import is_number, to_number, del_message, ded, clear_html, convert_date
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text, functions_mail_make
from tgbot.utils.text_functions import open_profile_admin, refill_open_admin, purchase_open_admin

router = Router(name=__name__)


# Поиск чеков и профилей
@router.message(F.text == "🔍 Поиск")
async def functions_find(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_find")
    await message.answer("<b>🔍 Отправьте айди/логин пользователя или номер чека</b>")


# Рассылка
@router.message(F.text == "📢 Рассылка")
async def functions_mail(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_mail_message")
    await message.answer(
        "<b>📢 Отправьте пост для рассылки пользователям</b>\n"
        "❕ Поддерживаются посты с любыми медиафайлами",
    )


################################################################################
################################### РАССЫЛКА ###################################
# Принятие текста для рассылки
@router.message(StateFilter("here_mail_message"))
async def functions_mail_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.update_data(here_mail_message=message)
    await state.set_state("here_mail_confirm")

    get_users = Userx.get_all()

    await message.reply(
        f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам данный пост?</b>",
        reply_markup=mail_confirm_finl(),
    )


# Подтверждение отправки рассылки
@router.callback_query(F.data.startswith("mail_confirm:"), StateFilter("here_mail_confirm"))
async def functions_mail_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    send_message = (await state.get_data())['here_mail_message']
    await state.clear()

    if get_status == "Yes":
        get_users = Userx.get_all()

        await call.message.edit_text(f"<b>📢 Рассылка началась... (0/{len(get_users)})</b>")

        await asyncio.create_task(functions_mail_make(bot, send_message, call))
    else:
        await call.message.edit_text("<b>📢 Вы отменили отправку рассылки ✅</b>")


################################################################################
##################################### ПОИСК ####################################
# Принятие айди/логина пользователя или чека для поиска
@router.message(F.text, StateFilter("here_find"))
@router.message(F.text.lower().startswith(('.find', 'find')))
async def functions_find_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    find_data = message.text.lower()

    if ".find" in find_data or "find" in find_data:
        if len(find_data.split(" ")) >= 2:
            if ".find" in find_data or "find" in find_data:
                find_data = message.text.split(" ")[1]
        else:
            return await message.answer(
                "<b>❌ Вы не указали поисковые данные</b>\n"
                "🔍 Отправьте айди/логин пользователя или номер чека",
            )

    if find_data.startswith("@") or find_data.startswith("#"):
        find_data = find_data[1:]

    if find_data.isdigit():
        get_user = Userx.get(user_id=find_data)
    else:
        get_user = Userx.get(user_login=find_data.lower())

    get_refill = Refillx.get(refill_receipt=find_data)
    get_purchase = Purchasesx.get(purchase_receipt=find_data)

    if get_user is None and get_refill is None and get_purchase is None:
        return await message.answer(
            "<b>❌ Данные не были найдены</b>\n"
            "🔍 Отправьте айди/логин пользователя или номер чека",
        )

    await state.clear()

    if get_user is not None:
        return await open_profile_admin(bot, message.from_user.id, get_user)

    if get_refill is not None:
        return await refill_open_admin(bot, message.from_user.id, get_refill)

    if get_purchase is not None:
        return await purchase_open_admin(bot, arSession, message.from_user.id, get_purchase)


################################################################################
############################## УПРАВЛЕНИЕ ПРОФИЛЕМ #############################
# Обновление профиля пользователя
@router.callback_query(F.data.startswith("admin_user_refresh:"))
async def functions_user_refresh(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    get_user = Userx.get(user_id=user_id)

    await state.clear()

    await del_message(call.message)
    await open_profile_admin(bot, call.from_user.id, get_user)


# Покупки пользователя
@router.callback_query(F.data.startswith("admin_user_purchases:"))
async def functions_user_purchases(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    get_user = Userx.get(user_id=user_id)
    get_purchases = Purchasesx.gets(user_id=user_id)[-10:]

    if len(get_purchases) < 1:
        return await call.answer("❗ У пользователя отсутствуют покупки", True)

    await call.answer("🎁 Последние 10 покупок")
    await del_message(call.message)

    for purchase in get_purchases:
        link_items = await upload_text(arSession, purchase.purchase_data)

        await call.message.answer(
            ded(f"""
                <b>🧾 Чек: <code>#{purchase.purchase_receipt}</code></b>
                🎁 Товар: <code>{purchase.purchase_position_name} | {purchase.purchase_count}шт | {purchase.purchase_price}₽</code>
                🕰 Дата покупки: <code>{convert_date(purchase.purchase_unix)}</code>
                🔗 Товары: <a href='{link_items}'>кликабельно</a>
            """)
        )

        await asyncio.sleep(0.2)

    await open_profile_admin(bot, call.from_user.id, get_user)


############################### БОНУСЫ ПОЛЬЗОВАТЕЛЯ ##############################
# Добавление бонуса пользователю
@router.callback_query(F.data.startswith("admin_user_bonus_add:"))
async def functions_user_bonus_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    await state.update_data(here_user=user_id)
    await state.set_state("here_user_bonus_add")

    await call.message.edit_text(
        "<b>🎁 Введите сумму бонуса</b>\n"
        "Этот бонус уменьшит сумму следующего заказа пользователя.",
        reply_markup=profile_edit_return_finl(user_id),
    )


# Принятие суммы бонуса
@router.message(F.text, StateFilter("here_user_bonus_add"))
async def functions_user_bonus_add_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    user_id = (await state.get_data())['here_user']

    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно</b>\n"
            "🎁 Введите сумму бонуса (число)",
            reply_markup=profile_edit_return_finl(user_id),
        )

    bonus_amount = to_number(message.text)

    if bonus_amount <= 0 or bonus_amount > 1_000_000_000:
        return await message.answer(
            "<b>❌ Сумма бонуса не может быть меньше 1 и больше 1 000 000 000</b>\n"
            "🎁 Введите сумму бонуса",
            reply_markup=profile_edit_return_finl(user_id),
        )

    await state.clear()

    get_user = Userx.get(user_id=user_id)
    new_bonus = round(get_user.user_balance + bonus_amount, 2)

    # Используем поле user_balance как «баланс бонусов»
    Userx.update(
        user_id,
        user_balance=new_bonus,
    )

    try:
        await bot.send_message(
            user_id,
            f"<b>🎁 Вам был начислен бонус <code>{message.text}</code></b>\n"
            "Он будет автоматически учтён при оформлении следующего заказа.",
        )
    except:
        ...

    await message.answer(
        f"👤 Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"🎁 Добавлен бонус: <code>{message.text}</code> | <code>{get_user.user_balance}</code> -> <code>{new_bonus}</code>"
    )

    get_user = Userx.get(user_id=user_id)
    await open_profile_admin(bot, message.from_user.id, get_user)


# Отправка сообщения пользователю
@router.callback_query(F.data.startswith("admin_user_message:"))
async def functions_user_user_message(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    await state.update_data(here_user_id=user_id)
    await state.set_state("here_user_message")

    await call.message.edit_text(
        "<b>💌 Введите сообщение для отправки</b>\n"
        "⚠️ Сообщение будет сразу отправлено пользователю.",
        reply_markup=profile_edit_return_finl(user_id),
    )


# Принятие сообщения для отправки пользователю
@router.message(F.text, StateFilter("here_user_message"))
async def functions_user_user_message_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    user_id = (await state.get_data())['here_user_id']
    await state.clear()

    get_message = "<b>💌 Сообщение от администратора:</b>\n" + f"<code>{clear_html(message.text)}</code>"
    get_user = Userx.get(user_id=user_id)

    try:
        await bot.send_message(user_id, get_message)
    except:
        await message.reply("<b>❌ Не удалось отправить сообщение</b>")
    else:
        await message.reply("<b>✅ Сообщение было успешно доставлено</b>")

    await open_profile_admin(bot, message.from_user.id, get_user)
