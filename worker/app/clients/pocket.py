from typing import Any, Dict, Optional

from loguru import logger

from app.clients.http_ import HttpClientABC


class PocketClient:
    def __init__(self, http_client: HttpClientABC, consumer_key: str):
        self._client = http_client
        self._consumer_key = consumer_key

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Accept": "application/json",
        }

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
