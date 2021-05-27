from app.core.clients.telegram import Telegram
from app.core.commands.delete_feed.repository import CommandDeleteFeedRepository
from app.schemas.message import Message


class CommandDeleteFeedService:
    def __init__(self, repository: CommandDeleteFeedRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def handle(self, update: Message) -> None:
        pass
