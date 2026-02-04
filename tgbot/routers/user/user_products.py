# -*- coding: utf-8 -*-
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest

from tgbot.database import Positionx, Categoryx, Itemx, Cartx, CartSizex
from tgbot.keyboards.inline_user_page import prod_item_category_swipe_fp, prod_item_position_swipe_fp
from tgbot.utils.const_functions import del_message
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import get_positions_items
from tgbot.utils.text_functions import position_open_user
from tgbot.database.db_item_sizes import ItemSizex
from tgbot.keyboards.inline_user_sizes import kb_sizes_for_item


router = Router(name=__name__)


async def _category_or_reload(call: CallbackQuery, category_id: int):
    """
    Если категория удалена/не существует — не падаем, а показываем список категорий заново.
    """
    cat = Categoryx.get(category_id=category_id)
    if cat is None:
        await call.answer("❌ Категория уже удалена или не существует. Обновляю список.", show_alert=True)
        try:
            await call.message.edit_text(
                "<b>🎁 Выберите нужный вам товар</b>",
                reply_markup=prod_item_category_swipe_fp(0),
            )
        except TelegramBadRequest:
            await call.message.answer(
                "<b>🎁 Выберите нужный вам товар</b>",
                reply_markup=prod_item_category_swipe_fp(0),
            )
        return None
    return cat


# --------- Показ категорий / позиций ----------
@router.callback_query(F.data.startswith("buy_category_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])
    await call.message.edit_text(
        "<b>🎁 Выберите нужный вам товар</b>",
        reply_markup=prod_item_category_swipe_fp(remover),
    )


@router.callback_query(F.data.startswith("buy_category_open:"))
async def user_buy_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = await _category_or_reload(call, category_id)
    if get_category is None:
        return

    get_positions = get_positions_items(category_id)

    if len(get_positions) >= 1:
        await del_message(call.message)
        await call.message.answer(
            f"<b>🎁 Текущая категория: <code>{get_category.category_name}</code></b>",
            reply_markup=prod_item_position_swipe_fp(remover, category_id),
        )
    else:
        await call.answer(f"❕ Товары в категории {get_category.category_name} отсутствуют", True, cache_time=5)


@router.callback_query(F.data.startswith("buy_position_swipe:"))
async def user_buy_position_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = await _category_or_reload(call, category_id)
    if get_category is None:
        return

    await del_message(call.message)
    await call.message.answer(
        f"<b>🎁 Текущая категория: <code>{get_category.category_name}</code></b>",
        reply_markup=prod_item_position_swipe_fp(remover, category_id),
    )


@router.callback_query(F.data.startswith("buy_position_open:"))
async def user_buy_position_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.clear()
    await del_message(call.message)
    await position_open_user(bot, call.from_user.id, position_id, remover)


# -------------------- Добавление в корзину --------------------
@router.callback_query(F.data.startswith("cart_add:"))
async def cart_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    parts = call.data.split(":")
    position_id = int(parts[1])
    count = int(parts[2]) if len(parts) > 2 else 1

    # Если для позиции заведены размеры — запрещаем добавление без выбора размера
    sizes = ItemSizex.gets(position_id)
    if sizes:
        return await call.answer("Сначала выберите размер через кнопку «📏 Выбрать размер»", show_alert=True)

    items = Itemx.gets(position_id=position_id)
    if len(items) < 1:
        return await call.answer("❗ Товара нет в наличии", True)

    # Добавление в корзину для позиций без размеров (старый режим)
    Cartx.add(
        user_id=call.from_user.id,
        position_id=position_id,
        count=count,
    )

    # Видимое сообщение пользователю + короткий алерт
    pos = Positionx.get(position_id=position_id)
    name = pos.position_name if pos else "Товар"
    await call.message.answer(f"✅ <b>{name}</b> x{count} добавлен(ы) в корзину.")
    await call.answer("Добавлено в корзину", cache_time=1)


@router.callback_query(F.data.startswith("size:open:"))
async def on_open_sizes(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    # формат: size:open:<position_id>
    parts = call.data.split(":")
    position_id = int(parts[2])

    # Показываем клавиатуру размеров вместо обычной клавиатуры товара
    await call.message.edit_reply_markup(reply_markup=kb_sizes_for_item(position_id))
    await call.answer(cache_time=1)


@router.callback_query(F.data.startswith("size:pick:"))
async def on_pick_size(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    # формат: size:pick:<position_id>:<size_id>
    parts = call.data.split(":")
    position_id = int(parts[2])
    size_id = int(parts[3])

    size = ItemSizex.get(size_id)
    if not size or size.qty <= 0:
        await call.answer("Нет в наличии 😢", show_alert=True)
        return

    # РЕЗЕРВ: сразу уменьшаем остаток выбранного размера (qty),
    # чтобы этот размер не могли купить другие, пока заказ не оформлен или не отменён.
    ItemSizex.set_qty(size_id, int(size.qty) - 1)

    # Сохраняем выбранный размер в корзину — по нему потом можно
    # восстановить остатки, если заказ/корзина будет отменён.
    Cartx.add(
        user_id=call.from_user.id,
        position_id=position_id,
        count=1,
        size_id=size.size_id,
        size_title=size.title,
    )

    # Видимое сообщение пользователю + короткий алерт
    pos = Positionx.get(position_id=position_id)
    name = pos.position_name if pos else "Товар"
    await call.message.answer(f"✅ <b>{name}</b>, размер <b>{size.title}</b> добавлен в корзину.")
    await call.answer("Добавлено в корзину", cache_time=1)

    # Обновляем клаву размеров (кол-во по размерам будет скорректировано при оформлении заказа)
    try:
        await call.message.edit_reply_markup(reply_markup=kb_sizes_for_item(position_id))
    except TelegramBadRequest:
        # Если Telegram считает, что разметка не изменилась — просто игнорируем эту ошибку
        pass


@router.callback_query(F.data.startswith("item:back:"))
async def on_item_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    # формат: item:back:<position_id>
    parts = call.data.split(":")
    position_id = int(parts[2])

    pos = Positionx.get(position_id=position_id)
    if not pos:
        await call.answer("Товар не найден", show_alert=True)
        return

    # Возвращаем стандартную клавиатуру карточки товара
    await call.message.edit_reply_markup(
        reply_markup=prod_item_position_swipe_fp(0, pos.category_id)
    )
    await call.answer(cache_time=1)
