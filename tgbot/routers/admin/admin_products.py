# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import get_admins
from tgbot.database import Categoryx, Itemx, Positionx, Userx, Purchasesx
from tgbot.keyboards.inline_admin import close_finl
from tgbot.keyboards.inline_admin_page import (
    category_edit_swipe_fp, position_add_swipe_fp,
    position_edit_category_swipe_fp, position_edit_swipe_fp,
    item_add_position_swipe_fp, item_add_category_swipe_fp,
    item_delete_swipe_fp
)
from tgbot.keyboards.inline_admin_products import (
    category_edit_delete_finl, position_edit_clear_finl,
    position_edit_delete_finl, position_edit_cancel_finl,
    category_edit_cancel_finl, products_removes_finl,
    products_removes_categories_finl, products_removes_positions_finl,
    products_removes_items_finl, item_add_finish_finl
)
from tgbot.services.api_discord import DiscordAPI
from tgbot.utils.const_functions import (
    clear_list, is_number, to_number, del_message, ded, get_unix, clear_html
)
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text
from tgbot.utils.text_functions import category_open_admin, position_open_admin, item_open_admin

router = Router(name=__name__)


# Создание новой категории
@router.message(F.text == "🗃 Создать категорию ➕")
async def prod_category_add(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await state.set_state("here_category_name")
    await message.answer("<b>🗃 Введите название для категории</b>")


# Выбор категории для редактирования
@router.message(F.text == "🗃 Изменить категорию 🖍")
async def prod_category_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()
    if len(get_categories) >= 1:
        await message.answer(
            "<b>🗃 Выберите категорию для изменения 🖍</b>",
            reply_markup=category_edit_swipe_fp(0),
        )
    else:
        await message.answer("<b>❌ Отсутствуют категории для изменения категорий</b>")


# Создание новой позиции
@router.message(F.text == "📁 Создать позицию ➕")
async def prod_position_add(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()
    if len(get_categories) >= 1:
        await message.answer(
            "<b>📁 Выберите категорию для позиции ➕</b>",
            reply_markup=position_add_swipe_fp(0),
        )
    else:
        await message.answer("<b>❌ Отсутствуют категории для создания позиции</b>")


# Выбор позиции для редактирования
@router.message(F.text == "📁 Изменить позицию 🖍")
async def prod_position_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()
    if len(get_categories) >= 1:
        await message.answer(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_category_swipe_fp(0),
        )
    else:
        await message.answer("<b>❌ Отсутствуют категории для изменения позиций</b>")


# Удаление категорий, позиций или товаров
@router.message(F.text == "❌ Удаление")
async def prod_removes(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await message.answer(
        "<b>🎁 Выберите раздел который хотите удалить ❌</b>\n",
        reply_markup=products_removes_finl(),
    )


################################################################################
############################### СОЗДАНИЕ КАТЕГОРИИ #############################
# Принятие названия категории для её создания
@router.message(F.text, StateFilter('here_category_name'))
async def prod_category_add_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "🗃 Введите название для категории",
        )

    await state.clear()

    category_id = get_unix()
    Categoryx.add(category_id, clear_html(message.text))

    await category_open_admin(bot, message.from_user.id, category_id, 0)


################################################################################
############################### ИЗМЕНЕНИЕ КАТЕГОРИИ ############################
# Страница выбора категорий для редактирования
@router.callback_query(F.data.startswith("category_edit_swipe:"))
async def prod_category_edit_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>🗃 Выберите категорию для изменения 🖍</b>",
        reply_markup=category_edit_swipe_fp(remover),
    )


# Выбор текущей категории для редактирования
@router.callback_query(F.data.startswith("category_edit_open:"))
async def prod_category_edit_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.clear()

    await del_message(call.message)
    await category_open_admin(bot, call.from_user.id, category_id, remover)


############################ САМО ИЗМЕНЕНИЕ КАТЕГОРИИ ##########################
# Изменение названия категории
@router.callback_query(F.data.startswith("category_edit_name:"))
async def prod_category_edit_name(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_category_edit_name")

    await del_message(call.message)

    await call.message.answer(
        "<b>🗃 Введите новое название для категории</b>",
        reply_markup=category_edit_cancel_finl(category_id, remover),
    )


# Принятие нового названия для категории
@router.message(F.text, StateFilter('here_category_edit_name'))
async def prod_category_edit_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    category_id = (await state.get_data())['here_category_id']
    remover = (await state.get_data())['here_remover']

    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "🗃 Введите новое название для категории",
            reply_markup=category_edit_cancel_finl(category_id, remover),
        )

    await state.clear()

    Categoryx.update(category_id, category_name=clear_html(message.text))
    await category_open_admin(bot, message.from_user.id, category_id, remover)


# Окно с уточнением удалить категорию
@router.callback_query(F.data.startswith("category_edit_delete:"))
async def prod_category_edit_delete(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await call.message.edit_text(
        "<b>❗ Вы действительно хотите удалить категорию и все её данные?</b>",
        reply_markup=category_edit_delete_finl(category_id, remover),
    )


# Отмена удаления категории
@router.callback_query(F.data.startswith("category_edit_delete_confirm:"))
async def prod_category_edit_delete_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    Categoryx.delete(category_id=category_id)
    Positionx.delete(category_id=category_id)
    Itemx.delete(category_id=category_id)

    await call.answer("🗃 Категория и все её данные были успешно удалены ✅")

    get_categories = Categoryx.get_all()
    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>🗃 Выберите категорию для изменения 🖍</b>",
            reply_markup=category_edit_swipe_fp(remover),
        )
    else:
        await del_message(call.message)


################################################################################
############################### ДОБАВЛЕНИЕ ПОЗИЦИИ #############################
# Cтраницы выбора категорий для расположения позиции
@router.callback_query(F.data.startswith("position_add_swipe:"))
async def prod_position_add_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>📁 Выберите категорию для позиции ➕</b>",
        reply_markup=position_add_swipe_fp(remover),
    )


# Выбор категории для создания позиции
@router.callback_query(F.data.startswith("position_add_open:"))
async def prod_position_add_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])

    await state.update_data(here_category_id=category_id)
    await state.set_state("here_position_name")

    await call.message.edit_text("<b>📁 Введите название для позиции</b>")


# Принятие названия для создания позиции
@router.message(F.text, StateFilter('here_position_name'))
async def prod_position_add_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "📁 Введите название для позиции",
        )

    await state.update_data(here_position_name=clear_html(message.text))
    await state.set_state("here_position_price")

    await message.answer("<b>📁 Введите цену для позиции</b>")


# Принятие цены позиции для её создания
@router.message(F.text, StateFilter('here_position_price'))
async def prod_position_add_price_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно</b>\n"
            "📁 Введите цену для позиции",
        )

    if to_number(message.text) > 10_000_000 or to_number(message.text) < 0:
        return await message.answer(
            "<b>❌ Цена не может быть меньше 0₽ или больше 10 000 000₽</b>\n"
            "📁 Введите цену для позиции",
        )

    await state.update_data(here_position_price=to_number(message.text))
    await state.set_state("here_position_desc")

    await message.answer(
        "<b>📁 Введите описание для позиции</b>\n"
        "❕ Вы можете использовать HTML разметку\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
    )


# Принятие описания позиции для её создания
@router.message(F.text, StateFilter('here_position_desc'))
async def prod_position_add_desc_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 1200:
        await message.answer(
            "<b>❌ Описание не может превышать 1200 символов</b>\n"
            "📁 Введите новое описание для позиции\n"
            "❕ Вы можете использовать HTML разметку\n"
            "❕ Отправьте <code>0</code> чтобы пропустить.",
        )

    try:
        if message.text != "0":
            await (await message.answer(message.text)).delete()
            position_desc = message.text
        else:
            position_desc = "None"
    except:
        return await message.answer(
            ded(f"""
                <b>❌ Ошибка синтаксиса HTML</b>
                📁 Введите описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
        )

    await state.update_data(here_position_desc=position_desc)
    await state.set_state("here_position_photo")

    await message.answer(
        "<b>📁 Отправьте изображение для позиции</b>\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
    )


# Принятие изображения для позиции при её создании
@router.message((F.text == "0") | F.photo, StateFilter('here_position_photo'))
async def prod_position_add_photo_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    category_id = state_data['here_category_id']
    position_name = clear_html(state_data['here_position_name'])
    position_price = to_number(state_data['here_position_price'])
    position_desc = state_data['here_position_desc']
    position_id = get_unix()
    position_photo = "None"
    await state.clear()

    if message.photo is not None:
        cache_message = await message.answer("<b>♻️ Подождите, фотография загружается...</b>")

        file_path = (await bot.get_file(message.photo[-1].file_id)).file_path
        photo_path = await bot.download_file(file_path)

        pay_image_status, pay_image_url = await (DiscordAPI(
            bot=bot,
            arSession=arSession,
            update=message,
        )).upload_photo(photo_path.read())

        if pay_image_status:
            position_photo = pay_image_url

        await del_message(cache_message)

    Positionx.add(
        category_id=category_id,
        position_id=position_id,
        position_name=position_name,
        position_price=position_price,
        position_desc=position_desc,
        position_photo=position_photo,
    )

    await position_open_admin(bot, message.from_user.id, position_id)


################################################################################
############################### ИЗМЕНЕНИЕ ПОЗИЦИИ ##############################
# Перемещение по страницам категорий для редактирования позиции
@router.callback_query(F.data.startswith("position_edit_category_swipe:"))
async def prod_position_edit_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>📁 Выберите позицию для изменения 🖍</b>",
        reply_markup=position_edit_category_swipe_fp(remover),
    )


# Выбор категории с нужной позицией
@router.callback_query(F.data.startswith("position_edit_category_open:"))
async def prod_position_edit_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])

    get_category = Categoryx.get(category_id=category_id)
    get_positions = Positionx.gets(category_id=category_id)

    if len(get_positions) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_swipe_fp(0, category_id),
        )
    else:
        await call.answer(f"📁 Позиции в категории {get_category.category_name} отсутствуют")


# Перемещение по страницам позиций для редактирования позиции
@router.callback_query(F.data.startswith("position_edit_swipe:"))
async def prod_position_edit_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Выберите позицию для изменения 🖍</b>",
        reply_markup=position_edit_swipe_fp(remover, category_id),
    )


# Выбор позиции для редактирования
@router.callback_query(F.data.startswith("position_edit_open:"))
async def prod_position_edit_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.clear()

    await del_message(call.message)
    await position_open_admin(bot, call.from_user.id, position_id)


############################ САМО ИЗМЕНЕНИЕ ПОЗИЦИИ ############################
# Изменение названия позиции
@router.callback_query(F.data.startswith("position_edit_name:"))
async def prod_position_edit_name(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_name")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Введите новое название для позиции</b>",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие названия позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_name'))
async def prod_position_edit_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']

    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "📁 Введите новое название для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_name=clear_html(message.text))
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение цены позиции
@router.callback_query(F.data.startswith("position_edit_price:"))
async def prod_position_edit_price(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_price")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Введите новую цену для позиции</b>",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие цены позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_price'))
async def prod_position_edit_price_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']

    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно</b>\n"
            "📁 Введите новую цену для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    if to_number(message.text) > 10_000_000 or to_number(message.text) < 0:
        return await message.answer(
            "<b>❌ Цена не может быть меньше 0₽ или больше 10 000 000₽</b>\n"
            "📁 Введите новую цену для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_price=to_number(message.text))
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение описания позиции
@router.callback_query(F.data.startswith("position_edit_desc:"))
async def prod_position_edit_desc(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_desc")

    await del_message(call.message)

    await call.message.answer(
        ded(f"""
            <b>📁 Введите новое описание для позиции</b>
            ❕ Вы можете использовать HTML разметку
            ❕ Отправьте <code>0</code> чтобы пропустить
        """),
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие описания позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_desc'))
async def prod_position_edit_desc_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    category_id = state_data['here_category_id']
    position_id = state_data['here_position_id']
    remover = state_data['here_remover']

    if len(message.text) > 1200:
        return await message.answer(
            ded(f"""
                <b>❌ Описание не может превышать 1200 символов</b>
                📁 Введите новое описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    try:
        if message.text != "0":
            await (await message.answer(message.text)).delete()
            position_desc = message.text
        else:
            position_desc = "None"
    except:
        return await message.answer(
            ded(f"""
                <b>❌ Ошибка синтаксиса HTML</b>
                📁 Введите новое описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_desc=position_desc)
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение изображения позиции
@router.callback_query(F.data.startswith("position_edit_photo:"))
async def prod_position_edit_photo(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_photo")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Отправьте новое изображение для позиции</b>\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие нового фото для позиции
@router.message((F.text == "0") | F.photo, StateFilter('here_position_edit_photo'))
async def prod_position_edit_photo_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()
    await state.clear()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']
    position_photo = "None"

    if message.photo is not None:
        cache_message = await message.answer("<b>♻️ Подождите, фотография загружается...</b>")

        file_path = (await bot.get_file(message.photo[-1].file_id)).file_path
        photo_path = await bot.download_file(file_path)

        pay_image_status, pay_image_url = await (DiscordAPI(
            bot=bot,
            arSession=arSession,
            update=message,
        )).upload_photo(photo_path.read())

        if pay_image_status:
            position_photo = pay_image_url

        await del_message(cache_message)

    Positionx.update(position_id, position_photo=position_photo)
    await position_open_admin(bot, message.from_user.id, position_id)


# Выгрузка товаров
@router.callback_query(F.data.startswith("position_edit_items:"))
async def prod_position_edit_items(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    get_position = Positionx.get(position_id=position_id)
    get_items = Itemx.gets(position_id=position_id)

    if len(get_items) >= 1:
        save_items = "\n\n".join([item.item_data for item in get_items])
        save_items = await upload_text(arSession, save_items)

        await call.message.answer(
            f"<b>🎁 Все товары позиции: <code>{get_position.position_name}</code>\n"
            f"🔗 Ссылка: <a href='{save_items}'>кликабельно</a></b>",
            reply_markup=close_finl(),
        )
        await call.answer(cache_time=5)
    else:
        await call.answer("❕ В данной позиции отсутствуют товары", True)


# Удаление позиции
@router.callback_query(F.data.startswith("position_edit_delete:"))
async def prod_position_edit_delete(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Вы действительно хотите удалить позицию? ❌</b>",
        reply_markup=position_edit_delete_finl(position_id, category_id, remover),
    )


# Подтверждение удаления позиции
@router.callback_query(F.data.startswith("position_edit_delete_confirm:"))
async def prod_position_edit_delete_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    Itemx.delete(position_id=position_id)
    Positionx.delete(position_id=position_id)

    await call.answer("📁 Вы успешно удалили позицию и её товары ✅")

    if len(Positionx.gets(category_id=category_id)) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_swipe_fp(remover, category_id),
        )
    else:
        await del_message(call.message)


# Очистка позиции
@router.callback_query(F.data.startswith("position_edit_clear:"))
async def prod_position_edit_clear(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Вы хотите удалить все товары в позиции?</b>",
        reply_markup=position_edit_clear_finl(position_id, category_id, remover),
    )


# Согласие очистики позиции
@router.callback_query(F.data.startswith("position_edit_clear_confirm:"))
async def prod_position_edit_clear_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    Itemx.delete(position_id=position_id)
    await call.answer("📁 Вы успешно удалили все товары в позиции ✅")

    await del_message(call.message)
    await position_open_admin(bot, call.from_user.id, position_id)


################################################################################
############################### ДОБАВЛЕНИЕ ТОВАРОВ #############################
# Перемещение по страницам категорий для добавления товаров
@router.callback_query(F.data.startswith("item_add_category_swipe:"))
async def prod_item_add_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])  # FIX
    await call.message.edit_text(
        "<b>🎁 Выберите позицию для товаров ➕</b>",
        reply_markup=item_add_category_swipe_fp(remover),
    )


# Выбор категории с нужной позицией
@router.callback_query(F.data.startswith("item_add_category_open:"))
async def prod_item_add_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = Categoryx.get(category_id=category_id)
    get_positions = Positionx.gets(category_id=category_id)

    await del_message(call.message)

    if len(get_positions) >= 1:
        await call.message.answer(
            "<b>🎁 Выберите позицию для товаров ➕</b>",
            reply_markup=item_add_position_swipe_fp(0, category_id),
        )
    else:
        await call.answer(f"🎁 Позиции в категории {get_category.category_name} отсутствуют")


# Перемещение по страницам позиций для добавления товаров
@router.callback_query(F.data.startswith("item_add_position_swipe:"))
async def prod_item_add_position_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await call.message.edit_text(
        "<b>🎁 Выберите позицию для товаров ➕</b>",
        reply_markup=item_add_position_swipe_fp(remover, category_id),
    )


# Выбор позиции для добавления товаров
@router.callback_query(F.data.startswith("item_add_position_open:"), flags={'rate': 0})
async def prod_item_add_position_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])

    await state.update_data(here_add_item_category_id=category_id)
    await state.update_data(here_add_item_position_id=position_id)
    await state.update_data(here_add_item_count=0)
    await state.set_state("here_add_items")

    await del_message(call.message)

    await call.message.answer(
        ded(f"""
            <b>🎁 Добавление товаров</b>

            ✅ Быстро количеством:
            ▪️ Отправь число <code>20</code> — добавит 20 шт (авто-данные)

            ✅ Списком (как раньше):
            ❗ Товары разделяются одной пустой строчкой. Пример:
            <code>Данные товара...

            Данные товара...

            Данные товара...</code>

            ❌ Отмена: отправь <code>0</code>
        """),
        reply_markup=item_add_finish_finl(position_id),
    )


# Завершение загрузки товаров
@router.callback_query(F.data.startswith('item_add_position_finish:'), flags={'rate': 0})
async def prod_item_add_finish(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])

    try:
        count_items = (await state.get_data())['here_add_item_count']
    except:
        count_items = 0

    await state.clear()

    await call.message.edit_reply_markup()
    await call.message.answer(
        "<b>🎁 Загрузка товаров была успешно завершена ✅\n"
        f"❕ Загружено товаров: <code>{count_items}шт</code></b>",
    )

    await position_open_admin(bot, call.from_user.id, position_id)


# Принятие данных товара (СПИСОК или КОЛИЧЕСТВО)
@router.message(F.text, StateFilter('here_add_items'), flags={'rate': 0})
async def prod_item_add_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    text = (message.text or "").strip()

    if text == "0":
        await state.clear()
        return await message.answer("<b>❌ Добавление товаров отменено</b>")

    cache_message = await message.answer("<b>⌛ Ждите, товары добавляются..</b>")

    state_data = await state.get_data()
    item_count = state_data.get('here_add_item_count', 0)
    category_id = state_data.get('here_add_item_category_id')
    position_id = state_data.get('here_add_item_position_id')

    # Режим "количеством": "50" / "50шт" / "50 шт"
    first = text.split()[0].replace("шт", "").strip().lower()
    if first.isdigit():
        qty = int(first)

        if qty <= 0:
            return await cache_message.edit_text(
                "<b>❌ Количество должно быть больше 0</b>",
                reply_markup=item_add_finish_finl(position_id),
            )

        if qty > 1000:
            return await cache_message.edit_text(
                "<b>❌ Слишком много за раз. Максимум: 1000</b>",
                reply_markup=item_add_finish_finl(position_id),
            )

        stamp = get_unix()
        get_items = [f"AUTO:{position_id}:{stamp}:{i+1}" for i in range(qty)]

        await state.update_data(here_add_item_count=item_count + qty)

        get_user = Userx.get(user_id=message.from_user.id)
        Itemx.add(
            user_id=get_user.user_id,
            category_id=category_id,
            position_id=position_id,
            item_datas=get_items,
        )

        return await cache_message.edit_text(
            f"<b>🎁 Товары в кол-ве <u>{qty}шт</u> были успешно добавлены ✅</b>",
            reply_markup=item_add_finish_finl(position_id),
        )

    # Режим "списком" (старый)
    get_items = clear_list(text.split("\n\n"))
    if len(get_items) < 1:
        return await cache_message.edit_text(
            "<b>❌ Пусто. Отправь число или список товаров</b>",
            reply_markup=item_add_finish_finl(position_id),
        )

    await state.update_data(here_add_item_count=item_count + len(get_items))

    get_user = Userx.get(user_id=message.from_user.id)
    Itemx.add(
        user_id=get_user.user_id,
        category_id=category_id,
        position_id=position_id,
        item_datas=get_items,
    )

    await cache_message.edit_text(
        f"<b>🎁 Товары в кол-ве <u>{len(get_items)}шт</u> были успешно добавлены ✅</b>",
        reply_markup=item_add_finish_finl(position_id),
    )


################################################################################
############################### УДАЛЕНИЕ ТОВАРОВ ###############################
# Страницы удаления товаров
@router.callback_query(F.data.startswith("item_delete_swipe:"))
async def prod_item_delete_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    get_items = Itemx.gets(position_id=position_id)
    get_position = Positionx.get(position_id=position_id)

    if len(get_items) >= 1:
        await del_message(call.message)

        await call.message.answer(
            "<b>🎁 Выберите товар для удаления</b>",
            reply_markup=item_delete_swipe_fp(remover, position_id, category_id),
        )
    else:
        await call.answer(f"🎁 Товары в позиции {get_position.position_name} отсутствуют", True)


# Удаление товара
@router.callback_query(F.data.startswith("item_delete_open:"))
async def prod_item_delete_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    item_id = call.data.split(":")[1]

    await del_message(call.message)
    await item_open_admin(bot, call.from_user.id, item_id, 0)


# Подтверждение удаления товара
@router.callback_query(F.data.startswith("item_delete_confirm:"))
async def prod_item_delete_confirm_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    item_id = call.data.split(":")[1]

    get_item = Itemx.get(item_id=item_id)
    get_items = Itemx.gets(position_id=get_item.position_id)

    Itemx.delete(item_id=item_id)

    await call.message.edit_text(
        ded(f"""
            <b>✅ Товар был успешно удалён</b>
            ➖➖➖➖➖➖➖➖➖➖
            🎁️ Товар: <code>{get_item.item_data}</code>
        """)
    )

    if len(get_items) >= 1:
        await call.message.answer(
            "<b>🎁 Выберите товар для удаления</b>",
            reply_markup=item_delete_swipe_fp(0, get_item.position_id, get_item.category_id),
        )


################################################################################
############################### УДАЛЕНИЕ РАЗДЕЛОВ ##############################
# Возвращение к меню удаления разделов
@router.callback_query(F.data == "prod_removes_return")
async def prod_removes_return(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>🎁 Выберите раздел который хотите удалить ❌</b>\n",
        reply_markup=products_removes_finl(),
    )


# Удаление всех категорий
@router.callback_query(F.data == "prod_removes_categories")
async def prod_removes_categories(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_categories = len(Categoryx.get_all())
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        ded(f"""
            <b>❌ Вы действительно хотите удалить все категории, позиции и товары?</b>
            🗃 Категорий: <code>{get_categories}шт</code>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """),
        reply_markup=products_removes_categories_finl(),
    )


# Подтверждение удаления всех категорий (позиций и товаров включительно)
@router.callback_query(F.data == "prod_removes_categories_confirm")
async def prod_removes_categories_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_categories = len(Categoryx.get_all())
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    Categoryx.clear()
    Positionx.clear()
    Itemx.clear()

    await call.message.edit_text(
        ded(f"""
            <b>✅ Вы успешно удалили все категории</b>
            🗃 Категорий: <code>{get_categories}шт</code>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """)
    )


# Удаление всех позиций
@router.callback_query(F.data == "prod_removes_positions")
async def prod_removes_positions(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        ded(f"""
            <b>❌ Вы действительно хотите удалить все позиции и товары?</b>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """),
        reply_markup=products_removes_positions_finl(),
    )


# Подтверждение удаления всех позиций (товаров включительно)
@router.callback_query(F.data == "prod_removes_positions_confirm")
async def prod_position_remove(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    Positionx.clear()
    Itemx.clear()

    await call.message.edit_text(
        ded(f"""
            <b>✅ Вы успешно удалили все позиции</b>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """)
    )


# Удаление всех товаров
@router.callback_query(F.data == "prod_removes_items")
async def prod_removes_items(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        f"<b>❌ Вы действительно хотите удалить все товары?</b>\n"
        f"🎁 Товаров: <code>{get_items}шт</code>",
        reply_markup=products_removes_items_finl(),
    )


# Согласие на удаление всех товаров
@router.callback_query(F.data == "prod_removes_items_confirm")
async def prod_item_remove(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_items = len(Itemx.get_all())

    Itemx.clear()

    await call.message.edit_text(
        f"<b>✅ Вы успешно удалили все товары</b>\n"
        f"🎁 Товаров: <code>{get_items}шт</code>"
    )


################################################################################
########################## ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ЗАКАЗА #########################
@router.callback_query(F.data.startswith("order_paid_ok:"))
async def admin_order_paid_ok(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    """
    Кнопка в группе заказов: админ подтверждает, что деньги получены.
    Новый формат: order_paid_ok:<user_id>:<order_id>:<count>:<total_int>:<bonus_used>
    Старый формат (для уже отправленных заявок): order_paid_ok:<user_id>:<order_id>
    """
    parts = call.data.split(":")
    if len(parts) < 3:
        return await call.answer("Некорректные данные заявки.", True)

    user_id = int(parts[1])
    order_id = parts[2]

    # По умолчанию (старые заявки) — 1 товар, без суммы/бонуса
    total_count = 1
    total_int = 0
    bonus_used = 0

    if len(parts) >= 6:
        # Новый формат с полной информацией
        try:
            total_count = int(parts[3])
            total_int = int(parts[4])          # фактически оплаченная сумма (после бонуса)
            bonus_used = int(parts[5])         # сколько бонусов было списано
        except ValueError:
            # Если по какой-то причине не смогли распарсить — продолжаем как старый формат
            total_count = 1
            total_int = 0
            bonus_used = 0

    # Только админы могут подтверждать
    if call.from_user.id not in get_admins():
        return await call.answer("У вас нет прав подтверждать оплату.", True)

    from tgbot.utils.text_functions import money

    try:
        # Если уже есть покупка с таким чеком — не дублируем
        existing = Purchasesx.get(purchase_receipt=order_id)
        if existing:
            return await call.answer("Этот заказ уже подтверждён ранее.", True)

        get_user = Userx.get(user_id=user_id)
        if not get_user:
            return await call.answer("Пользователь не найден в БД.", True)

        # Списываем бонусы (используем поле user_balance как «баланс бонусов»)
        balance_before = get_user.user_balance
        new_balance = max(0, balance_before - bonus_used)
        Userx.update(
            user_id,
            user_balance=new_balance,
        )

        # Регистрируем покупку в статистике как «ручной заказ по карте»
        Purchasesx.add(
            user_id=user_id,
            user_balance_before=balance_before,
            user_balance_after=new_balance,
            purchase_receipt=order_id,
            purchase_data=f"Manual card order #{order_id}",
            purchase_count=total_count,
            purchase_price=float(total_int),
            purchase_price_one=float(total_int) / total_count if total_count else float(total_int),
            purchase_position_id=0,
            purchase_position_name="MANUAL_CARD_ORDER",
            purchase_category_id=0,
            purchase_category_name="MANUAL",
        )

        # Обновляем сообщение в группе (видно, что оплата подтверждена)
        extra = ""
        if bonus_used > 0:
            extra = f"\n🎁 Списано бонусов: {money(bonus_used)}"
        await call.message.edit_text(
            call.message.text
            + "\n\n✅ Оплата подтверждена админом."
            + (f"\n💳 Оплачено: {money(total_int)}" if total_int > 0 else "")
            + extra
        )

        # Просто закрываем "крутилку" у нажатой кнопки
        await call.answer("Оплата отмечена как подтверждённая.", cache_time=1)

    except Exception as e:
        # Если что-то пошло не так — не даём кнопке крутиться бесконечно, показываем ошибку админу
        try:
            await call.answer("Ошибка при подтверждении оплаты.", show_alert=True)
            await call.message.answer(
                ded(f"""
                    <b>❌ Ошибка при подтверждении оплаты</b>
                    🧾 Заказ: <code>#{order_id}</code>
                    👤 TG ID: <code>{user_id}</code>
                    🔍 Ошибка: <code>{e}</code>
                """)
            )
        except Exception:
            ...
