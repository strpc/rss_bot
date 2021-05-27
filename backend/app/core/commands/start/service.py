from app.core.clients.telegram import Telegram
from app.core.commands.start.repository import CommandStartRepository
from app.schemas.message import Message


class CommandStartService:
    def __init__(self, repository: CommandStartRepository, telegram: Telegram):
        self._telegram = telegram
        self._repository = repository

    async def handle(self, update: Message):  # type: ignore
        pass
