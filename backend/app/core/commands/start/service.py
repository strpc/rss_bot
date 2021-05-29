from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandStartService(CommandServiceABC):
    def __init__(
        self,
        *,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._service_messages = service_messages

    async def handle(self, update: Message) -> None:
        await self._service_messages.send(update.message.chat.id, ServiceMessage.hello_user)
