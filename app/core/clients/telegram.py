import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.core.clients.requests_ import IClient

logger = logging.getLogger(__name__)


class ITelegram(ABC):
    @abstractmethod
    def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: bool = False
    ): ...


class Telegram(ITelegram):

    def __init__(self, client: IClient):
        self._client = client

    def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: bool = False
    ) -> httpx.Response:
        """Отправка сообщений пользователю"""
        method = "sendMessage"
        body = {
            "chat_id": chat_id,
            "text": text
        }
        if parse_mode:
            body['parse_mode'] = parse_mode
        if disable_web_page_preview:
            body['disable_web_page_preview'] = True
        return self._client.post(method=method, body=body)
