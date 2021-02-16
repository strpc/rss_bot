import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from httpx import Response

from app.core.clients import IClient
from app.project.settings import BASE_URL_TELEGRAM_API as BASE_URL


logger = logging.getLogger(__name__)


class ITelegram(ABC):
    @abstractmethod
    def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: bool = False,
    ) -> Response: ...


class Telegram(ITelegram):

    def __init__(self, token: str, client: IClient, base_url_api: Optional[str] = None):
        self._token = token
        self._client = client
        if base_url_api is not None:
            self._base_url = base_url_api[:-1] if base_url_api.endswith('/') else base_url_api
        else:
            self._base_url = BASE_URL[:-1] if BASE_URL.endswith('/') else BASE_URL

    def _get_url(self, method: str) -> str:
        method = method[1:] if method.startswith('/') else method
        return f"{self._base_url}/bot{self._token}/{method}"

    def _send_post_request(self, method: str, body: Dict) -> Response:
        url = self._get_url(method)
        return self._client.post(url=url, body=body)

    def send_message(
            self,
            chat_id: int,
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: bool = False,
    ) -> Response:
        """Отправка сообщений пользователю"""
        method = "sendMessage"
        body = {
            "chat_id": chat_id,
            "text": text
        }
        if parse_mode is not None:
            body['parse_mode'] = parse_mode
        if disable_web_page_preview is True:
            body['disable_web_page_preview'] = True
        return self._send_post_request(method=method, body=body)
