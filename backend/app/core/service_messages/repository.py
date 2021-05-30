from typing import Optional, Type

from aiocache import Cache

from app.core.clients.database import Database
from app.core.service_messages.models import ServiceMessage


class ServiceMessagesRepository:
    def __init__(self, database: Database, cache: Type[Cache]):
        self._db = database
        self._cache = cache(cache.MEMORY)
        self._cache_ttl = 5

    async def _get_message_from_cache(self, title: ServiceMessage) -> Optional[str]:
        cached_result = await self._cache.get(title)
        if cached_result is not None:
            return cached_result

    async def _set_cache_message(self, title: ServiceMessage, message: str) -> None:
        await self._cache.set(key=title, value=message, ttl=self._cache_ttl)

    async def get_message(self, title: ServiceMessage) -> Optional[str]:
        from_cache = await self._get_message_from_cache(title)
        if from_cache is not None:
            return from_cache

        query = """
        SELECT text
        FROM bot_service_message
        WHERE title = ?
        """
        row = await self._db.fetchone(query, (title,))
        if row is not None:
            message = row[0]  # type: ignore
            await self._set_cache_message(title, message)
            return message
