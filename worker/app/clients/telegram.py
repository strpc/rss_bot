import asyncio
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Dict, Optional

from loguru import logger

from app.clients.http_ import HttpClientABC, Response
from app.enums import ParseMode


class TelegramABC(ABC):
    @abstractmethod
    async def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: bool = False,
        attempt: int = 5,
        delay: int = 5,
    ) -> Response:
        ...


class Telegram(TelegramABC):
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
            json_body = response.json()
        except JSONDecodeError as error:
            logger.warning(error)
            json_body = None

        logger.error(
            "Request error. url: {}. status_code: {}, response: {}",
            url,
            response.status_code,
            json_body,
        )
        return response

    async def send_message(
        self,
        chat_id: int,
        text: str,
        *,
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

        url = self._format_url(method)
        return await self._send_post_request(url, body, attempt=attempt, delay=delay)

    async def send_raw_message(
        self,
        body: Dict[str, Any],
        *,
        attempt: int = 5,
        delay: int = 0,  # TODO: DEBUG MODE!
    ) -> Response:
        method = "sendMessage"
        url = self._format_url(method)
        return await self._send_post_request(url, body, attempt=attempt, delay=delay)
