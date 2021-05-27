from fastapi import Depends

from app.core.base_deps import get_database, get_telegram_client
from app.core.clients.database import Database
from app.core.clients.telegram import Telegram
from app.core.commands.list_feed.repository import CommandListFeedRepository
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_list_feed_repository(
    db: Database = Depends(get_database),
) -> CommandListFeedRepository:
    return CommandListFeedRepository(database=db)


def get_command_list_feed_service(
    repository: CommandListFeedRepository = Depends(get_command_list_feed_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandListFeedService:
    return CommandListFeedService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )
