from typing import Optional

from app.core.clients.database import Database
from app.core.service_messages.models import ServiceMessage


class ServiceMessagesRepository:
    def __init__(self, database: Database):
        self._db = database

    async def get_message(self, title: ServiceMessage) -> Optional[str]:
        query = """
        SELECT text
        FROM bot_service_message
        WHERE title = ?
        """
        row = await self._db.fetchone(query, (title,))
        if row is not None:
            return row[0]  # type: ignore
