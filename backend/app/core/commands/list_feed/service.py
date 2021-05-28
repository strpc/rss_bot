from app.core.clients.telegram import Telegram
from app.core.feeds.service import FeedsService
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandListFeedService:
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._feeds_service = feeds_service
        self._service_messages = service_messages

    async def handle(self, update: Message) -> None:
        pass
