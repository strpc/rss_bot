from app.core.clients.telegram import Telegram
from app.core.service_messages import models
from app.core.service_messages.repository import ServiceMessagesRepository


class ServiceMessagesService:
    def __init__(self, repository: ServiceMessagesRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def send(self, chat_id: int, service_message: models.ServiceMessage):  # type: ignore
        pass
