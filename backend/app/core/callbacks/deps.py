from fastapi import Depends

from app.core.base_deps import get_telegram_client
from app.core.callbacks.service import CallbackService
from app.core.clients.telegram import Telegram
from app.core.integration.deps import get_external_services
from app.core.integration.service import ExternalServices
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService
from app.core.users.deps import get_users_service
from app.core.users.service import UsersService


def get_callback_service(
    external_services: ExternalServices = Depends(get_external_services),
    users_service: UsersService = Depends(get_users_service),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CallbackService:
    return CallbackService(
        users_service=users_service,
        external_services=external_services,
        service_messages=service_messages,
        telegram=telegram,
    )
