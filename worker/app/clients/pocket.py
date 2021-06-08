from typing import Any, Dict, Optional

from loguru import logger

from app.clients.http_ import HttpClientABC


class PocketIntegrationError(Exception):
    def __init__(
        self,
        *,
        pocket_error_code: int,
        http_status_code: int,
    ):
        errors_map = {
            138: "Missing consumer key.",
            152: "Invalid consumer key.",
            181: "Invalid redirect uri.",
            182: "Missing code.",
            185: "Code not found.",
            158: "User rejected code.",
            159: "Already used code.",
            199: "Pocket server issue.",
            000: "Pocket error code not found.",
        }
        self.pocket_error_code = pocket_error_code
        self.pocket_error_message = errors_map.get(self.pocket_error_code, errors_map[000])
        self.http_status_code = http_status_code
        super(PocketIntegrationError, self).__init__(self.pocket_error_message)

    def __str__(self) -> str:
        return self.pocket_error_message


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
            logger.error(
                "Ошибка при получении access-токена. status_code={} headers={}",
                response.status_code,
                response.headers,
            )
            try:
                error_code = int(response.headers.get("X-Error-Code", "000"))
            except ValueError:
                error_code = 000
            raise PocketIntegrationError(
                pocket_error_code=error_code,
                http_status_code=response.status_code,
            )
        return response.json()
