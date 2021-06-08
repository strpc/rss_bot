from typing import Any, Dict, Optional

from app.clients.pocket import PocketClient


class PocketService:
    def __init__(self, client: PocketClient):
        self._client = client

    async def get_access_token(self, request_token: str) -> Optional[Dict[str, Any]]:
        return await self._client.get_access_token(request_token)
