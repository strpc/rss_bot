from fastapi import Depends

from app.config import MainConfig
from app.core.base_deps import get_config, get_telegram_client
from app.core.clients.telegram import Telegram
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.feeds.deps import get_feeds_service
from app.core.feeds.service import FeedsService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_add_feed_service(
    feeds_service: FeedsService = Depends(get_feeds_service),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
    config: MainConfig = Depends(get_config),
) -> CommandAddFeedService:
    return CommandAddFeedService(
        feeds_service=feeds_service,
        telegram=telegram,
        service_messages=service_messages,
        limit_feed=config.app.limit_feed,
    )
