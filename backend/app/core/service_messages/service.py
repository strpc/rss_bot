from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.service_messages import models
from app.core.service_messages.repository import ServiceMessagesRepository


class ServiceMessagesService:
    def __init__(self, repository: ServiceMessagesRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def send(self, chat_id: int, service_message: models.ServiceMessage):  # type: ignore
        text = await self._repository.get_message(service_message)

        if text is None:
            logger.error("Сервисное сообщение {} не найдено в базе.", service_message)
            text = "Произошла ошибка. Повторите запрос позже."

        await self._telegram.send_message(chat_id, text)
        logger.debug("Пользователю отправлено сервисное сообщение {}", service_message)
