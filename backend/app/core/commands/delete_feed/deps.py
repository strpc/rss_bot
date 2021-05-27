from fastapi import Depends

from app.core.base_deps import get_database, get_telegram_client
from app.core.clients.database import Database
from app.core.clients.telegram import Telegram
from app.core.commands.delete_feed.repository import CommandDeleteFeedRepository
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_delete_feed_repository(
    db: Database = Depends(get_database),
) -> CommandDeleteFeedRepository:
    return CommandDeleteFeedRepository(database=db)


def get_command_delete_feed_service(
    repository: CommandDeleteFeedRepository = Depends(get_command_delete_feed_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandDeleteFeedService:
    return CommandDeleteFeedService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )
