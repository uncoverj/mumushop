# -*- coding: utf-8 -*-
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from tgbot.states import AdminSizes

from tgbot.database import Positionx
from tgbot.database.db_item_sizes import ItemSizex
from tgbot.keyboards.inline_admin_sizes import kb_admin_sizes, kb_admin_size_edit
from tgbot.utils.const_functions import del_message, is_number
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.text_functions import position_open_admin
from tgbot.states import AdminSizes  # ✅ твой StatesGroup

router = Router(name=__name__)


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery):
    await call.answer(cache_time=2)


@router.callback_query(F.data.startswith("asize:list:"))
async def asize_list(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[2])
    await state.clear()

    pos = Positionx.get(position_id=position_id)
    if not pos:
        return await call.answer("Позиция не найдена", show_alert=True)

    await call.message.answer(
        f"<b>📏 Размеры позиции:</b> <code>{pos.position_name}</code>",
        reply_markup=kb_admin_sizes(position_id),
    )
    await call.answer(cache_time=1)


@router.callback_query(F.data.startswith("asize:back:"))
async def asize_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[2])
    await state.clear()
    await del_message(call.message)
    await position_open_admin(bot, call.from_user.id, position_id)


@router.callback_query(F.data.startswith("asize:add:"))
async def asize_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[2])

    await state.clear()
    await state.update_data(position_id=position_id)
    await state.set_state(AdminSizes.add_title)

    await call.message.answer(
        "<b>📏 Введите название размера</b>\n"
        "Примеры: <code>S</code>, <code>M</code>, <code>XL</code>, <code>52</code>, <code>54</code>",
    )
    await call.answer(cache_time=1)


@router.message(F.text, StateFilter(AdminSizes.add_title))
async def asize_title_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    title = (message.text or "").strip()
    if len(title) > 20:
        return await message.answer("<b>❌ Слишком длинно (макс 20 символов). Введи короче.</b>")

    await state.update_data(title=title)
    await state.set_state(AdminSizes.add_qty)

    await message.answer("<b>Введите количество (число)</b>\nНапример: <code>3</code>")


@router.message(F.text, StateFilter(AdminSizes.add_qty))
async def asize_qty_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer("<b>❌ Нужно число. Введи количество ещё раз.</b>")

    qty = int(float(message.text))
    if qty < 0:
        qty = 0

    data = await state.get_data()
    position_id = int(data["position_id"])
    title = data["title"]

    ItemSizex.add(item_id=position_id, title=title, qty=qty)

    await state.clear()

    await message.answer("<b>✅ Размер добавлен</b>", reply_markup=kb_admin_sizes(position_id))


@router.callback_query(F.data.startswith("asize:open:"))
async def asize_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    size = ItemSizex.get(size_id)
    if not size:
        return await call.answer("Размер не найден", show_alert=True)

    await call.message.answer(
        f"<b>📏 Размер:</b> <code>{size.title}</code>\n"
        f"<b>Остаток:</b> <code>{size.qty}шт</code>",
        reply_markup=kb_admin_size_edit(position_id, size_id),
    )
    await call.answer(cache_time=1)


@router.callback_query(F.data.startswith("asize:rename:"))
async def asize_rename(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    await state.clear()
    await state.update_data(position_id=position_id, size_id=size_id)
    await state.set_state(AdminSizes.rename)

    await call.message.answer("<b>✏️ Введите новое название размера</b>")
    await call.answer(cache_time=1)


@router.message(F.text, StateFilter(AdminSizes.rename))
async def asize_rename_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    title = (message.text or "").strip()
    if len(title) > 20:
        return await message.answer("<b>❌ Слишком длинно (макс 20 символов). Введи короче.</b>")

    data = await state.get_data()
    position_id = int(data["position_id"])
    size_id = int(data["size_id"])

    ItemSizex.update(size_id, title=title)
    await state.clear()

    await message.answer("<b>✅ Название обновлено</b>", reply_markup=kb_admin_sizes(position_id))


@router.callback_query(F.data.startswith("asize:setqty:"))
async def asize_setqty(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    await state.clear()
    await state.update_data(position_id=position_id, size_id=size_id)
    await state.set_state(AdminSizes.set_qty)

    await call.message.answer("<b>🧮 Введите новое количество (число)</b>")
    await call.answer(cache_time=1)


@router.message(F.text, StateFilter(AdminSizes.set_qty))
async def asize_setqty_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer("<b>❌ Нужно число. Введи количество ещё раз.</b>")

    qty = int(float(message.text))
    if qty < 0:
        qty = 0

    data = await state.get_data()
    position_id = int(data["position_id"])
    size_id = int(data["size_id"])

    ItemSizex.update(size_id, qty=qty)
    await state.clear()

    await message.answer("<b>✅ Количество обновлено</b>", reply_markup=kb_admin_sizes(position_id))


@router.callback_query(F.data.startswith("asize:inc:"))
async def asize_inc(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    size = ItemSizex.get(size_id)
    if not size:
        return await call.answer("Размер не найден", show_alert=True)

    ItemSizex.update(size_id, qty=int(size.qty) + 1)
    await call.answer("✅ +1", cache_time=1)
    await call.message.answer("Обновлено ✅", reply_markup=kb_admin_sizes(position_id))


@router.callback_query(F.data.startswith("asize:dec:"))
async def asize_dec(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    size = ItemSizex.get(size_id)
    if not size:
        return await call.answer("Размер не найден", show_alert=True)

    new_qty = int(size.qty) - 1
    if new_qty < 0:
        new_qty = 0

    ItemSizex.update(size_id, qty=new_qty)
    await call.answer("✅ -1", cache_time=1)
    await call.message.answer("Обновлено ✅", reply_markup=kb_admin_sizes(position_id))


@router.callback_query(F.data.startswith("asize:del:"))
async def asize_del(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    _, _, position_id, size_id = call.data.split(":")
    position_id = int(position_id)
    size_id = int(size_id)

    ItemSizex.delete(size_id)
    await call.answer("🗑 Удалено", show_alert=True)
    await call.message.answer("Список размеров:", reply_markup=kb_admin_sizes(position_id))
