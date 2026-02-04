from aiogram import Bot
from tgbot.data.config import CURRENCY_SYMBOL


def tg_user_link(user_id: int, username: str | None) -> str:
    return f"https://t.me/{username.lstrip('@')}" if username else f"tg://user?id={user_id}"


async def send_order_to_tg(
    bot: Bot,
    chat_id: int,
    order_id: str,
    user_id: int,
    username: str | None,
    firstname: str | None,
    product_name: str,
    price,          # можно число или строка
    count: int,
    comment: str = "",
):
    link = tg_user_link(user_id, username)

    # Если price пришёл числом — добавим валюту тут
    if isinstance(price, (int, float)):
        price_text = f"{int(price)} {CURRENCY_SYMBOL}"
    else:
        price_text = str(price)

    text = (
        "🛒 НОВЫЙ ЗАКАЗ (без оплаты)\n"
        f"🆔 Заявка: #{order_id}\n"
        f"👤 Клиент: {firstname or '-'} (@{username or 'нет'})\n"
        f"🧾 TG ID: {user_id}\n"
        f"🔗 Написать: {link}\n\n"
        f"📦 Товар: {product_name}\n"
        f"🔢 Кол-во: {count}\n"
        f"💰 Сумма: {price_text}\n"
    )

    if comment.strip():
        text += f"\n📝 Комментарий: {comment.strip()}"

    await bot.send_message(chat_id, text)
