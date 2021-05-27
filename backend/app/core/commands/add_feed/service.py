from app.core.clients.telegram import Telegram
from app.core.commands.add_feed.repository import CommandAddFeedRepository
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandAddFeedService:
    def __init__(
        self,
        *,
        repository: CommandAddFeedRepository,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._repository = repository
        self._service_messages = service_messages

    async def handle(self, update: Message) -> None:
        pass
