from loguru import logger

from app.clients.telegram import Telegram
from app.core.service_messages import models
from app.core.service_messages.repository import InternalMessagesRepository


DEFAULT_INTERNAL_ERROR = "Произошла ошибка. Повторите запрос позже."


class InternalMessagesService:
    def __init__(self, repository: InternalMessagesRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def send(self, chat_id: int, service_message: models.InternalMessages):  # type: ignore
        text = await self._repository.get_message(service_message)

        if text is None:
            logger.error("Сервисное сообщение {} не найдено в базе.", service_message)
            text = DEFAULT_INTERNAL_ERROR

        await self._telegram.send_message(chat_id, text)
        logger.debug("Пользователю отправлено сервисное сообщение {}", service_message)
