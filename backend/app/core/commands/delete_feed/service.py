from app.core.clients.telegram import Telegram
from app.core.commands.delete_feed.repository import CommandDeleteFeedRepository
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandDeleteFeedService:
    def __init__(
        self,
        *,
        repository: CommandDeleteFeedRepository,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._repository = repository
        self._telegram = telegram
        self._service_messages = service_messages

    async def handle(self, update: Message) -> None:
        pass
