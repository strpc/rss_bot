from typing import Optional, Union

from loguru import logger

from app.api.schemas.callback import Callback
from app.api.schemas.message import Message
from app.core.users.models import User, UserIntegration
from app.core.users.repository import UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository):
        self._repository = repository

    async def get_user(self, chat_id: int) -> Optional[User]:
        logger.info("Поиск юзера в БД...")
        return await self._repository.get_user(chat_id)

    async def create_user(self, new_user: User) -> int:
        logger.info("Создаем нового юзера...")
        return await self._repository.create_user(new_user)

    async def disable_user(self, chat_id: int) -> None:
        logger.info("Отключение юзера chat_id={} ...", chat_id)
        return await self._repository.disable_user(chat_id=chat_id)

    async def get_or_create(self, update: Union[Message, Callback]) -> User:
        if isinstance(update, Message):
            chat_id = update.message.chat.id
        else:
            chat_id = update.callback_query.user.id

        user = await self.get_user(chat_id)
        if user is not None:
            logger.info("Юзер найден.")
            return user

        logger.info("Юзер не найден. Создаем нового юзера...")
        new_user = User(
            chat_id=update.message.chat.id,
            first_name=update.message.chat.first_name,
            last_name=update.message.chat.last_name,
            username=update.message.chat.username,
        )
        user_id = await self.create_user(new_user)
        logger.info("Юзер создан.")
        new_user.id = user_id
        return new_user

    async def activate_user(self, chat_id: int) -> None:
        logger.info("Активация юзера...")
        await self._repository.activate_user(chat_id)
        logger.info("Юзер активирован.")

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        return await self._repository.get_user_integration(chat_id)
