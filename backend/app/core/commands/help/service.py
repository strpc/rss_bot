from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService
from app.reporters_errors import get_telegram_reporter


telegram_reporter = get_telegram_reporter()


class CommandHelpService(CommandServiceABC):
    def __init__(
        self,
        *,
        telegram: Telegram,
        internal_messages_service: InternalMessagesService,
    ):
        self._telegram = telegram
        self._internal_messages_service = internal_messages_service

    @telegram_reporter(as_attached=True)
    async def handle(self, update: Update) -> None:
        await self._internal_messages_service.send(
            update.chat_id,
            InternalMessages.help,
        )
