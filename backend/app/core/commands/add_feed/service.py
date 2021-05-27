from app.core.clients.telegram import Telegram
from app.core.commands.add_feed.repository import CommandAddFeedRepository
from app.schemas.message import Message


class CommandAddFeedService:
    def __init__(self, repository: CommandAddFeedRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def handle(self, update: Message) -> None:
        pass
