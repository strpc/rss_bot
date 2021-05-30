from typing import Type

from aiocache import Cache
from fastapi import Depends

from app.core.base_deps import get_cache_type, get_database, get_telegram_client
from app.core.clients.database import Database
from app.core.clients.telegram import Telegram
from app.core.service_messages.repository import ServiceMessagesRepository
from app.core.service_messages.service import ServiceMessagesService


def get_service_messages_repository(
    db: Database = Depends(get_database),
    cache: Type[Cache] = Depends(get_cache_type),
) -> ServiceMessagesRepository:
    return ServiceMessagesRepository(database=db, cache=cache)


def get_service_messages_service(
    repository: ServiceMessagesRepository = Depends(get_service_messages_repository),
    telegram: Telegram = Depends(get_telegram_client),
) -> ServiceMessagesService:
    return ServiceMessagesService(repository=repository, telegram=telegram)
