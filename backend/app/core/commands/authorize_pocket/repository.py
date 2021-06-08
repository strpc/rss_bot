from app.core.clients.database import Database


class PocketAuthRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def _get_user_id(self, chat_id: int) -> int:
        query = f"""
        SELECT id
        FROM bot_users
        WHERE chat_id = {self._paramstyle}
        """
        row = await self._db.fetchone(query, (chat_id,))
        if row is not None:
            return row[0]  # type: ignore

    async def save_request_token(self, chat_id: int, request_token: str) -> None:
        user_id = await self._get_user_id(chat_id)
        if user_id is None:
            return

        query = f"""
        INSERT INTO bot_pocket_integration (user_id, request_token, active, added, updated)
        VALUES ({self._paramstyle}, {self._paramstyle}, true, datetime('now'), datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
        request_token={self._paramstyle},
        active=true,
        added=datetime('now'),
        updated=datetime('now'),
        access_token=null
        """
        await self._db.execute(query, (user_id, request_token, request_token))
