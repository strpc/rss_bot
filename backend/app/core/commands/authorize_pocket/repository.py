from typing import Optional

from app.core.clients.database import Database


class PocketAuthRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def _get_user_id(self, chat_id: int) -> int:
        query = f"""
        SELECT id
        FROM bot_users
        WHERE
            chat_id = {self._paramstyle}
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

    async def get_access_token(self, chat_id: int) -> Optional[str]:
        user_id = await self._get_user_id(chat_id)
        if user_id is None:
            return

        query = f"""
        SELECT access_token
        FROM bot_pocket_integration
        WHERE
            user_id = {self._paramstyle}
            AND active = true
        """
        row = await self._db.fetchone(query, (user_id,))
        if row is not None:
            return row[0]  # type: ignore

    async def disable_pocket_integration(self, chat_id: int) -> None:
        user_id = await self._get_user_id(chat_id)
        if user_id is None:
            return

        query = f"""
        UPDATE bot_pocket_integration
        SET
            updated = datetime('now'),
            active = false
        WHERE
            user_id = {self._paramstyle}
               """
        await self._db.execute(query, (user_id,))
