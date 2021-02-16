import logging
from abc import ABC, abstractmethod
from time import sleep
from typing import Dict, Optional

import httpx

from app.project.settings import (API_BASE_URL, ATTEMPT_REQUEST, DELAY_REQUEST,
                                  RSS_BOT_TOKEN)

logger = logging.getLogger(__name__)
API_BASE_URL = API_BASE_URL[:-1] if API_BASE_URL.endswith('/') else API_BASE_URL
REQUEST_URL = f"{API_BASE_URL}/bot{RSS_BOT_TOKEN}/"


class Telegram(ABC):
    @abstractmethod
    def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: bool = False
    ): ...


class ClientABC(ABC):
    @abstractmethod
    def get(self, method: str, params: Dict, attempt=ATTEMPT_REQUEST): ...

    @abstractmethod
    def post(
            self,
            method: str,
            params=None,
            body=None,
            data=None,
            attempt=ATTEMPT_REQUEST
    ): ...


class Client(ClientABC):
    """Обертка над запросами в API"""

    @staticmethod
    def _method_edit(method: str) -> str:
        return method[1:] if method.startswith('/') else method

    def get(self, method: str, params: Dict, attempt=ATTEMPT_REQUEST) -> httpx.Response:
        """Обертка над get-запросом"""
        r = httpx.get(url=REQUEST_URL + self._method_edit(method), params=params)

        if r.status_code != 200 and attempt:
            sleep(DELAY_REQUEST)
            attempt -= 1
            self.get(method, params, attempt)

        else:
            logger.error(
                'Request error. url: %s. params: %s, status_code: %s, response: %s',
                REQUEST_URL + method, params, r.status_code, r.json()
            )
        return r

    def post(
            self,
            method: str,
            params=None,
            body=None,
            data=None,
            attempt=ATTEMPT_REQUEST
    ) -> httpx.Response:
        """Обертка над post-запросом"""
        r = httpx.post(
            url=REQUEST_URL + self._method_edit(method), json=body, params=params, data=data
        )
        if r.status_code == 200:
            return r

        elif (
                r.status_code != 200
                and r.json().get('description') != "Forbidden: bot was blocked by the user"
                and attempt
        ):
            sleep(DELAY_REQUEST)
            attempt -= 1
            return self.post(method, params, body, data, attempt)

        else:
            logger.error(
                'Post request error. url: %s. params: %s, body: %s, data: %s, status_code: %s, '
                'response: %s', REQUEST_URL + method, params, body, bool(data), r.status_code,
                r.json()
            )
            return r


class TelegramClient(Telegram):

    def __init__(self, client: Client):
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
