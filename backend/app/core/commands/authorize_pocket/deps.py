from fastapi import Depends

from app.core.base_deps import get_database, get_pocket_client, get_telegram_client
from app.core.clients.database import Database
from app.core.clients.pocket import PocketClient
from app.core.clients.telegram import Telegram
from app.core.commands.authorize_pocket.repository import PocketAuthRepository
from app.core.commands.authorize_pocket.service import AuthorizePocketService
from app.core.service_messages.deps import get_service_messages_service
from app.core.service_messages.service import ServiceMessagesService


def get_authorize_pocket_repository(db: Database = Depends(get_database)) -> PocketAuthRepository:
    return PocketAuthRepository(database=db)


def get_authorize_pocket_service(
    repository: PocketAuthRepository = Depends(get_authorize_pocket_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
    pocket_client: PocketClient = Depends(get_pocket_client),
) -> AuthorizePocketService:
    return AuthorizePocketService(
        telegram=telegram,
        pocket_client=pocket_client,
        service_messages=service_messages,
        repository=repository,
    )
