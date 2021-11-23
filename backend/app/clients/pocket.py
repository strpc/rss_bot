from typing import Any, Dict, Optional

from httpx import Response
from loguru import logger

from app.clients.http_ import HttpClientABC


BASE_AUTHORIZE_POCKET_URL = "https://getpocket.com/auth/authorize"


class PocketError(Exception):
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
        super(PocketError, self).__init__(self.pocket_error_message)

    def __str__(self) -> str:
        return self.pocket_error_message


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

    async def _send_post_request(self, url: str, headers: Dict[str, Any], body: Any) -> Response:
        logger.debug("Отправляем post запрос body={}\nheaders={}", body, headers)
        return await self._client.post(url, headers=headers, body=body)

    @staticmethod
    def _handle_error(response: Response) -> None:
        try:
            error_code = int(response.headers.get("X-Error-Code", "000"))
        except ValueError:
            error_code = 000
        raise PocketError(
            pocket_error_code=error_code,
            http_status_code=response.status_code,
        )

    async def get_request_token(self) -> Optional[str]:
        url = "https://getpocket.com/v3/oauth/request"
        body = {
            "consumer_key": self._consumer_key,
            "redirect_uri": self._redirect_url,
        }
        response = await self._send_post_request(url, headers=self._get_headers(), body=body)

        if response.status_code != 200:
            logger.error("Ошибка при получении request-токена. headers={}", response.headers)
            return None
        return response.json().get("code")

    async def get_auth_url(self, request_token: str) -> str:
        return (
            f"{BASE_AUTHORIZE_POCKET_URL}"
            f"?request_token={request_token}&redirect_uri={self._redirect_url}"
        )

    async def get_access_token(self, request_token: str) -> Optional[Dict[Any, Any]]:
        url = "https://getpocket.com/v3/oauth/authorize"
        body = {
            "consumer_key": self._consumer_key,
            "code": request_token,
        }
        response = await self._send_post_request(url, headers=self._get_headers(), body=body)
        if response.status_code != 200:
            logger.error(
                "Ошибка при получении access-токена. status_code={} headers={}",
                response.status_code,
                response.headers,
            )
            self._handle_error(response)
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

        response = await self._send_post_request(api_url, headers=self._get_headers(), body=body)
        if response.status_code != 200:
            logger.error(
                "{} статус-код при отправке новой записи в Pocket. access_token={}. url={}",
                response.status_code,
                access_token,
                url,
            )
            self._handle_error(response)
