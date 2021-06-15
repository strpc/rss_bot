import asyncio
from json import JSONDecodeError
from typing import Dict, List, Optional

from loguru import logger

from app.core.clients.http_ import HttpClientABC, Response
from app.schemas.enums import ParseMode
from app.schemas.message import Button


class TelegramUserBlocked(Exception):
    pass


class Telegram:
    def __init__(
        self,
        *,
        token: str,
        client: HttpClientABC,
        base_url_api: str = "https://api.telegram.org",
    ):
        self._token = token
        self._client = client
        self._base_url = base_url_api[:-1] if base_url_api.endswith("/") else base_url_api

    def _format_url(self, method: str) -> str:
        return f"{self._base_url}/bot{self._token}/{method}"

    async def _send_post_request(
        self,
        url: str,
        body: Dict,
        *,
        attempt: int,
        delay: int,
    ) -> Response:
        response = await self._client.post(url=url, body=body)
        if response.status_code == 200:
            return response

        if attempt > 0:
            await asyncio.sleep(delay)
            attempt -= 1
            await self._send_post_request(url, body, attempt=attempt, delay=delay)

        try:
            response_body = response.json()
        except JSONDecodeError as error:
            logger.warning(error)
            response_body = None

        logger.error(
            "Request error. body: {}.\nurl:\n{}.\nstatus_code: {},\nresponse: {}",
            body,
            url,
            response.status_code,
            response_body,
        )
        if (
            response_body
            and response_body.get("description")
            and response_body["description"] == "Forbidden: bot was blocked by the user"
        ):
            raise TelegramUserBlocked
        return response

    async def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        inline_keyboard: Optional[List[Button]] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: bool = False,
        attempt: int = 5,
        delay: int = 0,  # TODO: DEBUG MODE!
    ) -> Response:
        """Отправка сообщений пользователю."""
        method = "sendMessage"
        body = {"chat_id": chat_id, "text": text}

        if parse_mode is not None:
            body["parse_mode"] = parse_mode

        if disable_web_page_preview:
            body["disable_web_page_preview"] = True

        if inline_keyboard is not None:
            body["reply_markup"] = {
                "inline_keyboard": [[button.dict() for button in inline_keyboard]],
            }

        url = self._format_url(method)
        return await self._send_post_request(url, body, attempt=attempt, delay=delay)

    async def update_buttons(
        self,
        *,
        chat_id: int,
        message_id: int,
        inline_keyboard: List[Button],
        attempt: int = 5,
        delay: int = 0,  # TODO: DEBUG MODE!
    ) -> Response:
        method = "editMessageReplyMarkup"

        body = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": [[button.dict() for button in inline_keyboard]]},
        }
        url = self._format_url(method)
        return await self._send_post_request(url, body, attempt=attempt, delay=delay)
