from app.api.schemas.message import Message
from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService


class CommandStartService(CommandServiceABC):
    def __init__(
        self,
        *,
        telegram: Telegram,
        internal_messages_service: InternalMessagesService,
    ):
        self._telegram = telegram
        self._internal_messages_service = internal_messages_service

    async def handle(self, update: Message) -> None:
        await self._internal_messages_service.send(
            update.message.chat.id,
            InternalMessages.hello_user,
        )
