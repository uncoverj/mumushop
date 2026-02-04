# -*- coding: utf-8 -*-
import asyncio
import json
import configparser
from io import BytesIO
from typing import Union, Optional

import ujson
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiohttp import FormData

from tgbot.database import Settingsx
from tgbot.utils.misc_functions import send_admins
from tgbot.utils.const_functions import gen_id
from tgbot.utils.misc.bot_models import ARS


class DiscordAPI:
    """
    Прямой Discord Webhook API (без djimbo.dev)
    """

    def __init__(
        self,
        bot: Bot,
        arSession: ARS,
        update: Union[Message, CallbackQuery] = None,
        webhook_url: Optional[str] = None,
        skipping_error: bool = False,
    ):
        # 1) webhook из settings.ini
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini", encoding="utf-8")
        webhook_from_ini = ""
        if cfg.has_section("settings"):
            webhook_from_ini = cfg["settings"].get("discord_webhook", "").strip()

        # 2) если передали webhook_url — он важнее
        if webhook_url:
            url = webhook_url.strip()
        # 3) иначе из ini
        elif webhook_from_ini:
            url = webhook_from_ini
        # 4) иначе из БД (если проект так хранит)
        else:
            s = Settingsx.get()
            url = (getattr(s, "misc_discord_webhook_url", "") or "").strip()

        self.bot = bot
        self.arSession = arSession
        self.update = update
        self.skipping_error = skipping_error

        self.webhook_username = "Shop Bot"
        self.webhook_url = self._normalize(url)
        self.enabled = bool(self.webhook_url)

    @staticmethod
    def _normalize(url: str) -> str:
        if not url:
            return ""
        url = url.strip()

        # допускаем ID/TOKEN
        if "/" in url and url.split("/")[0].isdigit() and not url.startswith("http"):
            return "https://discord.com/api/webhooks/" + url

        # допускаем discord.com/api/webhooks/...
        if url.startswith("discord.com/") or url.startswith("discordapp.com/"):
            url = "https://" + url

        if url.startswith("https://discord.com/api/webhooks/") or url.startswith("https://discordapp.com/api/webhooks/"):
            return url

        return ""

    async def error_account_admin(self, error_code: str = "Unknown"):
        if self.skipping_error:
            return
        await send_admins(
            self.bot,
            "<b>🖼 Дискорд вебхук недоступен. Замените webhook</b>\n"
            f"❗️ Ошибка: <code>{error_code}</code>"
        )

    async def check(self) -> tuple[bool, str]:
        if not self.enabled:
            return False, ""

        ok, data = await self._request(self.webhook_url, "GET")

        if ok and isinstance(data, dict):
            return True, data.get("name", "Webhook")

        return False, ""

    async def upload_photo(self, photo_data: Union[BytesIO, bytes], photo_name: str = None) -> tuple[bool, str]:
        """
        Загружает фото в Discord и возвращает URL attachment.
        """
        if not self.enabled:
            return False, "None"

        if photo_name is None:
            photo_name = str(gen_id(24))

        if (not photo_name.endswith(".png")) and (not photo_name.endswith(".jpg")) and (not photo_name.endswith(".jpeg")):
            photo_name = f"{photo_name}.png"

        payload = {"username": self.webhook_username, "content": ""}

        data = FormData()
        data.add_field("payload_json", ujson.dumps(payload))
        data.add_field("file", photo_data, filename=photo_name)

        # ✅ wait=true — чтобы Discord вернул JSON с attachments
        url = self.webhook_url + "?wait=true"

        ok, resp = await self._request(url, "POST", data)

        if ok and isinstance(resp, dict):
            at = resp.get("attachments") or []
            if at and isinstance(at, list) and at[0].get("url"):
                return True, at[0]["url"]

        return False, "None"

    async def _request(self, request_url: str, request_method: str, request_data=None):
        session = await self.arSession.get_session()
        await asyncio.sleep(0.2)

        try:
            response = await session.request(
                method=request_method,
                url=request_url,
                data=request_data,
                headers={},
                ssl=False,
            )

            raw = (await response.read()).decode(errors="ignore").strip()

            # ✅ Discord иногда отвечает 204 No Content — это не ошибка
            if response.status == 204:
                return True, {}

            if not raw:
                await self.error_account_admin(f"EMPTY_RESPONSE ({response.status})")
                return False, "EMPTY_RESPONSE"

            try:
                data = json.loads(raw)
            except Exception:
                await self.error_account_admin(f"NOT_JSON ({response.status}) {raw[:120]}")
                return False, "NOT_JSON"

            if 200 <= response.status < 300:
                return True, data

            await self.error_account_admin(f"{response.status} - {str(data)[:200]}")
            return False, data

        except Exception as ex:
            await self.error_account_admin(str(ex))
            return False, str(ex)


class DiscordDJ:
    """
    Заглушка для совместимости проекта.
    Раньше этот класс тянул ссылки с djimbo.dev — мы это убрали.
    Если где-то в коде вызывается export_forevercdn()/export_webhook(),
    вернём 'None', чтобы ничего не падало.
    """

    def __init__(self, arSession: ARS, bot: Bot):
        self.arSession = arSession
        self.bot = bot

    async def export_webhook(self) -> str:
        return "None"

    async def export_forevercdn(self) -> str:
        return "None"
