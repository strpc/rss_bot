from app.core.clients.telegram import Telegram
from app.schemas.message import Message


class DeleteFeedCommand:
    def __init__(self, telegram: Telegram):
        self._telegram = telegram

    async def handle(self, update: Message, repository):
        pass
