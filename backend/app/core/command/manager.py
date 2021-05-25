from fastapi import Depends

from app.core import deps
from app.core.clients.telegram import Telegram
from app.core.command.add_feed.service import AddFeedCommand
from app.core.command.delete_feed.service import DeleteFeedCommand
from app.core.command.list_feed.service import ListFeedCommand
from app.core.command.start.service import StartCommand
from app.schemas.message import Message


class CommandManager:
    @staticmethod
    async def start(
        update: Message,
        telegram: Telegram = Depends(deps.get_telegram),
        repository: str = "qwe",
    ):
        await StartCommand(telegram).handle(update, repository)

    @staticmethod
    async def add_feed(
        update: Message,
        telegram: Telegram = Depends(deps.get_telegram),
        repository: str = "qwe",
    ):
        await AddFeedCommand(telegram).handle(update, repository)

    @staticmethod
    async def list_feed(
        update: Message,
        telegram: Telegram = Depends(deps.get_telegram),
        repository: str = "qwe",
    ):
        await ListFeedCommand(telegram).handle(update, repository)

    @staticmethod
    async def delete_feed(
        update: Message,
        telegram: Telegram = Depends(deps.get_telegram),
        repository: str = "qwe",
    ):
        await DeleteFeedCommand(telegram).handle(update, repository)
