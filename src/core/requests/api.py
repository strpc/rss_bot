from abc import ABC, abstractmethod
from time import sleep
from typing import Dict
import logging

import httpx

from src.project.settings import BOT_TOKEN, API_BASE_URL, ATTEMPT_REQUEST, DELAY_REQUEST


logger = logging.getLogger(__name__)
API_BASE_URL = API_BASE_URL[:-1] if API_BASE_URL.endswith('/') else API_BASE_URL
REQUEST_URL = f"{API_BASE_URL}/bot{BOT_TOKEN}/"


class Client(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    def __method_edit(method: str) -> str:
        return method[1:] if method.startswith('/') else method

    def get(self, method: str, params: Dict, attempt=ATTEMPT_REQUEST) -> httpx.Response:
        """Обертка над get-запросом"""
        r = httpx.get(url=REQUEST_URL + self.__method_edit(method), params=params)

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
            self, method: str, params=None, body=None, data=None, attempt=ATTEMPT_REQUEST
    ) -> httpx.Response:
        """Обертка над post-запросом"""
        r = httpx.post(
            url=REQUEST_URL + self.__method_edit(method), json=body, params=params, data=data
        )
        if r.status_code != 200 and attempt:
            sleep(DELAY_REQUEST)
            attempt -= 1
            self.post(method, params, body, data, attempt)

        else:
            logger.error(
                'Post request error. url: %s. params: %s, body: %s, data: %s, status_code: %s, '
                'response: %s', REQUEST_URL + method, params, body, bool(data), r.status_code,
                r.json()
            )
        return r


class Request(Client):
    def __init__(self, chat_id: int):
        super().__init__()
        self.chat_id = chat_id

    def send_message(self, text: str):
        """Отправка сообщений пользователю"""
        method = "sendMessage"
        body = {
            "chat_id": self.chat_id,
            "text": text
        }
        self.post(method=method, body=body)
