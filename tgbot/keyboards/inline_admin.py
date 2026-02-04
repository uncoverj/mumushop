# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database import Settingsx
from tgbot.utils.const_functions import ikb


################################################################################
#################################### ПРОЧЕЕ ####################################
# Удаление сообщения
def close_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(ikb("❌ Закрыть", data="close_this"))
    return keyboard.as_markup()


# Рассылка
def mail_confirm_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        ikb("✅ Отправить", data="mail_confirm:Yes"),
        ikb("❌ Отменить", data="mail_confirm:Not"),
    )
    return keyboard.as_markup()


# Поиск профиля пользователя
def profile_edit_finl(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🎁 Добавить бонус", data=f"admin_user_bonus_add:{user_id}"),
    ).row(
        ikb("🎁 Покупки", data=f"admin_user_purchases:{user_id}"),
        ikb("💌 Отправить СМС", data=f"admin_user_message:{user_id}"),
    ).row(
        ikb("🔄 Обновить", data=f"admin_user_refresh:{user_id}"),
    )

    return keyboard.as_markup()


# Возвращение к профилю пользователя
def profile_edit_return_finl(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(ikb("❌ Отменить", data=f"admin_user_refresh:{user_id}"))
    return keyboard.as_markup()


################################################################################
############################## ПЛАТЕЖНЫЕ СИСТЕМЫ ###############################
# ✅ Платежи ОТКЛЮЧЕНЫ. Оставляем заглушки, чтобы бот не падал,
# если где-то в коде ещё вызываются эти функции.

def payment_yoomoney_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(ikb("🚫 Платежи отключены", data="close_this"))
    return keyboard.as_markup()


def payment_cryptobot_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(ikb("🚫 Платежи отключены", data="close_this"))
    return keyboard.as_markup()


################################################################################
################################## НАСТРОЙКИ ###################################
# Основные настройки (БЕЗ "Платёжных систем" и без Discord webhook)
def settings_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    get_settings = Settingsx.get()

    # Текст для FAQ
    if get_settings.misc_faq == "None":
        faq_kb = ikb("Не установлено ❌", data="settings_edit_faq")
    else:
        faq_kb = ikb(f"{get_settings.misc_faq[:15]}... ✅", data="settings_edit_faq")

    # Контакты поддержки
    if get_settings.misc_support == "None":
        support_kb = ikb("Не установлена ❌", data="settings_edit_support")
    else:
        support_kb = ikb(f"@{get_settings.misc_support} ✅", data="settings_edit_support")

    # Скрытие категорий без товаров
    if get_settings.misc_hide_category == "True":
        hide_category_kb = ikb("Скрыты", data="settings_edit_hide_category:False")
    else:
        hide_category_kb = ikb("Отображены", data="settings_edit_hide_category:True")

    # Скрытие позиций без товаров
    if get_settings.misc_hide_position == "True":
        hide_position_kb = ikb("Скрыты", data="settings_edit_hide_position:False")
    else:
        hide_position_kb = ikb("Отображены", data="settings_edit_hide_position:True")

    keyboard.row(
        ikb("❔ FAQ", data="..."), faq_kb,
    ).row(
        ikb("☎️ Поддержка", data="..."), support_kb,
    ).row(
        ikb("🎁 Категории без товаров", data="..."), hide_category_kb,
    ).row(
        ikb("🎁 Позиции без товаров", data="..."), hide_position_kb,
    )

    # ❌ тут НЕ добавляем "Платёжные системы"
    # ❌ тут НЕ добавляем "Discord Webhook"

    return keyboard.as_markup()


# Выключатели (убрали "Пополнения")
def settings_status_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    get_settings = Settingsx.get()

    status_work_kb = ikb("Включены ✅", data="settings_status_work:False")
    status_buy_kb = ikb("Включены ✅", data="settings_status_buy:False")

    if get_settings.status_work == "False":
        status_work_kb = ikb("Выключены ❌", data="settings_status_work:True")
    if get_settings.status_buy == "False":
        status_buy_kb = ikb("Выключены ❌", data="settings_status_buy:True")

    keyboard.row(
        ikb("⛔ Тех. работы", data="..."), status_work_kb,
    ).row(
        ikb("🎁 Покупки", data="..."), status_buy_kb,
    )

    # ❌ "💰 Пополнения" убрали полностью

    return keyboard.as_markup()
