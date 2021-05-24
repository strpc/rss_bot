import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from app.core.clients import IRequests
from app.project.settings import BASE_URL_TELEGRAM_API as BASE_URL
from httpx import Response


logger = logging.getLogger(__name__)


class ITelegram(ABC):
    @abstractmethod
    def send_message(
        self,
        *,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
    ) -> Response:
        ...


class Telegram(ITelegram):
    def __init__(
        self,
        *,
        token: str,
        client: IRequests,
        base_url_api: Optional[str] = None,
    ):
        self._token = token
        self._client = client
        if base_url_api is not None:
            self._base_url = base_url_api[:-1] if base_url_api.endswith("/") else base_url_api
        else:
            self._base_url = BASE_URL[:-1] if BASE_URL.endswith("/") else BASE_URL

    def _get_url(self, method: str) -> str:
        method = method[1:] if method.startswith("/") else method
        return f"{self._base_url}/bot{self._token}/{method}"

    def _send_post_request(self, method: str, body: Dict) -> Response:
        url = self._get_url(method)
        return self._client.post(url=url, body=body)

    def send_message(
        self,
        *,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
    ) -> Response:
        """Отправка сообщений пользователю"""
        method = "sendMessage"
        body = {"chat_id": chat_id, "text": text}
        if parse_mode is not None:
            body["parse_mode"] = parse_mode
        if disable_web_page_preview is True:
            body["disable_web_page_preview"] = True
        return self._send_post_request(method=method, body=body)


# if __name__ == "__main__":
#     title = "*Мониторинг NetApp Volumes через HTTP*\n\n"
#     text = (
#         "Хабы: Блог компании ДомКлик, *nix, API Всем привет. В продолжение прош_лой стат"
#         "ьи, связанной с костылями и SSH для мониторинга места и метрик производительности досту"
#         "пных нам томов на NetApp, хочу поделиться и описать более прав"
#         "ильный способ мониторин...\n\nhttps://habr.com/ru/post/542122/".replace(
#             "_", "\\_"
#         )
#         .replace("*", "\\*")
#         .replace("[", "\\[")
#         .replace("`", "\\`")
#         .replace(".", "\\.")
#     )
#     telegram = Telegram(token=RSS_BOT_TOKEN, client=Requests())
#     telegram.send_message(chat_id=126471094, text=title + text, parse_mode="MarkdownV2")
