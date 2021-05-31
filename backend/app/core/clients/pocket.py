from typing import Any, Dict, Optional

from loguru import logger

from app.core.clients.http_ import HttpClientABC


class PocketClient:
    def __init__(self, http_client: HttpClientABC, consumer_key: str, redirect_url: str):
        self._client = http_client
        self._consumer_key = consumer_key
        self._redirect_url = redirect_url

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Accept": "application/json",
        }

    async def get_request_token(self) -> Optional[str]:
        url = "https://getpocket.com/v3/oauth/request"
        body = {
            "consumer_key": self._consumer_key,
            "redirect_uri": self._redirect_url,
        }
        response = await self._client.post(url, headers=self._get_headers(), body=body)

        if response.status_code != 200:
            logger.error("Ошибка при получении request-токена. headers={}", response.headers)
            return None
        request_token = response.json().get("code")
        return request_token

    async def get_auth_url(self, request_token: str) -> str:
        url = (
            f"https://getpocket.com/auth/authorize?request_token="
            f"{request_token}&redirect_uri={self._redirect_url}"
        )
        return url

    async def get_access_token(self, request_token: str) -> Optional[Dict[Any, Any]]:
        url = "https://getpocket.com/v3/oauth/authorize"
        body = {
            "consumer_key": self._consumer_key,
            "code": request_token,
        }
        response = await self._client.post(url, headers=self._get_headers(), body=body)
        if response.status_code != 200:
            logger.error("Ошибка при получении access-токена. headers={}", response.headers)
            return None
        return response.json()

    async def add_item(self, *, access_token: str, url: str, tags: Optional[str] = None) -> None:
        api_url = "https://getpocket.com/v3/add"
        body = {
            "consumer_key": self._consumer_key,
            "access_token": access_token,
            "url": url,
        }
        if tags is not None:
            body["tags"] = tags

        response = await self._client.post(api_url, headers=self._get_headers(), body=body)
        if response.status_code != 200:
            logger.warning("{} статус-код при отправки новой записи в Pocket", response.status_code)
