from typing import Dict, List, Optional

from app.clients.database import Database


class PocketRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = database.paramstyle

    async def get_access_token(self, chat_id: int) -> Optional[str]:
        query = f"""
        SELECT access_token
        FROM bot_pocket_integration
        JOIN bot_users ON bot_pocket_integration.user_id = bot_users.id
        AND bot_users.chat_id == {self._paramstyle}
        """
        row = await self._db.fetchone(query, (chat_id,))
        if row is not None:
            return row[0]  # type: ignore

    async def get_new_request_token(self) -> Optional[List[Dict[str, str]]]:
        query = """
        SELECT
            request_token as pocket_request_token,
            user_id as user_id
        FROM bot_pocket_integration
        WHERE
            active is true
        AND access_token is null
        """
        return await self._db.fetchall(query, as_dict=True)  # type: ignore

    async def disable_pocket_integration(
        self,
        *,
        user_id: int,
        error_code: Optional[int],
        error_message: Optional[str],
        status_code: Optional[int],
    ) -> None:
        query = f"""
        UPDATE bot_pocket_integration
        SET
            error_code = {self._paramstyle},
            error_message = {self._paramstyle},
            status_code = {self._paramstyle},
            updated = datetime('now'),
            active = false
        WHERE
            user_id = {self._paramstyle}
        """
        await self._db.execute(query, (error_code, error_message, status_code, user_id))

    async def update_pocket_meta(
        self,
        user_id: int,
        access_token: str,
        username: str,
    ) -> None:
        query = f"""
        UPDATE bot_pocket_integration
        SET
            access_token = {self._paramstyle},
            username = {self._paramstyle},
            updated = datetime('now')
        WHERE
            user_id = {self._paramstyle}
        """
        await self._db.execute(query, (access_token, username, user_id))
