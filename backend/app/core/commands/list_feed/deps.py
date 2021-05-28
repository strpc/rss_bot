from fastapi import Depends

from app.core.base_deps import get_telegram_client
from app.core.clients.telegram import Telegram
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.feeds.deps import get_feeds_service
from app.core.feeds.service import FeedsService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_list_feed_service(
    feeds_service: FeedsService = Depends(get_feeds_service),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandListFeedService:
    return CommandListFeedService(
        feeds_service=feeds_service,
        telegram=telegram,
        service_messages=service_messages,
    )
