from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger

from app.core.users.models import User, UserIntegration
from app.core.users.repository import UsersRepository
from app.schemas.callback import Callback
from app.schemas.message import Message


class UsersService:
    def __init__(self, repository: UsersRepository):
        self._repository = repository

    async def get_user(self, chat_id: int) -> Optional[User]:
        logger.info("Поиск юзера в БД...")
        return await self._repository.get_user(chat_id)

    async def create_user(self, new_user: User) -> None:
        logger.info("Создаем нового юзера...")
        await self._repository.create_user(new_user)

    async def get_or_create(self, update: Union[Message, Callback]) -> User:
        if isinstance(update, Message):
            chat_id = update.message.chat.id
        else:
            chat_id = update.callback_query.user.id

        user = await self.get_user(chat_id)
        if user is not None:
            logger.info("Юзер найден.")
            return user

        logger.info("Юзер не найден.")
        new_user = User(
            chat_id=update.message.chat.id,
            first_name=update.message.chat.first_name,
            last_name=update.message.chat.last_name,
            username=update.message.chat.username,
        )
        await self.create_user(new_user)
        logger.info("Юзер создан.")
        return new_user

    async def activate_user(self, chat_id: int) -> None:
        logger.info("Активация юзера...")
        await self._repository.activate_user(chat_id)
        logger.info("Юзер активирован.")

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        return await self._repository.get_active_users()

    async def get_new_request_token(self) -> Optional[List[Dict]]:
        return await self._repository.get_new_request_token()

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        return await self._repository.get_user_integration(chat_id)

    async def get_entry_url(self, entry_id: int) -> Optional[str]:
        return await self._repository.get_entry_url(entry_id)

    async def get_access_token(self, chat_id: int) -> Optional[str]:
        return await self._repository.get_access_token(chat_id=chat_id)

    async def update_access_token(
        self,
        user_id: int,
        access_token: Dict[str, Any],
    ) -> None:
        token = access_token.get("access_token")
        username = access_token.get("username")
        await self._repository.update_pocket_meta(
            user_id=user_id,
            access_token=token,  # type: ignore
            username=username,  # type: ignore
        )

    async def disable_pocket_integration(
        self,
        *,
        user_id: int,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        logger.info("Отключаем интеграцию у юзера user_id={}...", user_id)
        await self._repository.disable_pocket_integration(
            user_id=user_id,
            error_code=error_code,
            error_message=error_message,
            status_code=status_code,
        )
