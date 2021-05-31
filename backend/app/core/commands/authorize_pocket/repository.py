from app.core.clients.database import Database


class PocketAuthRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def save_request_token(self, chat_id: int, request_token: str) -> None:
        query = f"""
        INSERT INTO x3 table (chat_id, request_token)
        VALUES ({self._paramstyle}, {self._paramstyle})
        """
        await self._db.execute(query, (chat_id, request_token))
