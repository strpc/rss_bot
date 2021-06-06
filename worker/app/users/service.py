from typing import Optional, Tuple

from app.users.models import User, UserIntegration
from app.users.repository import UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository):
        self._repository = repository

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        return await self._repository.get_active_users()

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        return await self._repository.get_user_integration(chat_id)
