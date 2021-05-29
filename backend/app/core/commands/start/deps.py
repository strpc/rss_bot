from fastapi import Depends

from app.core.base_deps import get_telegram_client
from app.core.clients.telegram import Telegram
from app.core.commands.start.service import CommandStartService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_start_service(
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandStartService:
    return CommandStartService(
        telegram=telegram,
        service_messages=service_messages,
    )
