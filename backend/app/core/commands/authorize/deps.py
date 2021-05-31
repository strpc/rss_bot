from fastapi import Depends

from app.core.base_deps import get_telegram_client
from app.core.clients.telegram import Telegram
from app.core.commands.authorize.service import AuthorizeService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_command_authorize_service(
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> AuthorizeService:
    return AuthorizeService(
        telegram=telegram,
        service_messages=service_messages,
    )
