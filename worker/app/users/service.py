from typing import Any, Dict, Optional, Tuple

from app.users.models import User, UserIntegration
from app.users.repository import UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository):
        self._repository = repository

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        return await self._repository.get_active_users()

    async def get_new_request_token(self) -> Optional[Tuple[str, ...]]:
        return await self._repository.get_new_request_token()

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        return await self._repository.get_user_integration(chat_id)

    async def update_access_token(
        self,
        request_token: str,
        access_token: Dict[str, Any],
    ) -> None:
        token = access_token.get("access_token")
        username = access_token.get("username")
        await self._repository.update_pocket_meta(
            request_token=request_token,
            access_token=token,  # type: ignore
            username=username,  # type: ignore
        )
