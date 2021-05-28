from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.commands.start.repository import CommandStartRepository
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandStartService:
    def __init__(
        self,
        *,
        repository: CommandStartRepository,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._repository = repository
        self._service_messages = service_messages

    async def handle(self, update: Message) -> None:
        logger.debug("hello command /start")
        await self._service_messages.send(update.message.chat.id, ServiceMessage.hello_user)
