# - *- coding: utf- 8 - *-
from aiogram import Dispatcher, F
from tgbot.states import AdminSizes

from tgbot.routers import main_errors, main_start, main_missed
from tgbot.routers.admin import admin_menu, admin_functions, admin_products, admin_settings, admin_sizes, admin_payments  # ✅
from tgbot.routers.user import user_menu, user_products, order_cancel
from tgbot.utils.misc.bot_filters import IsAdmin


def register_all_routers(dp: Dispatcher):
    dp.message.filter(F.chat.type == "private")
    # Раньше callback'и глобально ограничивались приватными чатами.
    # Для подтверждения оплаты в админской группе/чате нужно принимать callback'и и из других типов чатов,
    # поэтому общий фильтр по chat.type для callback_query убираем.

    # Админские фильтры
    admin_menu.router.message.filter(IsAdmin())
    admin_functions.router.message.filter(IsAdmin())
    admin_settings.router.message.filter(IsAdmin())
    admin_products.router.message.filter(IsAdmin())
    admin_sizes.router.message.filter(IsAdmin())      # ✅ ВАЖНО
    admin_sizes.router.callback_query.filter(IsAdmin())  # ✅ ВАЖНО (иначе “кнопка недействительна”)

    # Обязательные
    dp.include_router(main_errors.router)
    dp.include_router(main_start.router)

    # Пользовательские
    dp.include_router(user_menu.router)
    dp.include_router(user_products.router)
    dp.include_router(order_cancel.router)

    # Админские
    dp.include_router(admin_menu.router)
    dp.include_router(admin_functions.router)
    dp.include_router(admin_settings.router)
    dp.include_router(admin_products.router)
    dp.include_router(admin_sizes.router)  # ✅ ВАЖНО
    dp.include_router(admin_payments.router)

    # Обязательные
    dp.include_router(main_missed.router)
