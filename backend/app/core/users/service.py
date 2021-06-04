from typing import Optional, Union

from loguru import logger

from app.core.users.models import User
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
