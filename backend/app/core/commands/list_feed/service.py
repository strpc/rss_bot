from app.core.clients.telegram import Telegram
from app.core.commands.list_feed.repository import CommandListFeedRepository
from app.schemas.message import Message


class CommandListFeedService:
    def __init__(self, repository: CommandListFeedRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def handle(self, update: Message) -> None:
        pass
