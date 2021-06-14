from typing import Dict, List, Optional, Tuple

from pydantic import parse_obj_as

from app.core.clients.database import Database
from app.core.users.models import User, UserIntegration


class UsersRepository:
    def __init__(self, database: Database):
        self._db = database
        self._paramstyle = self._db.paramstyle

    async def get_user(self, chat_id: int) -> Optional[User]:
        query = f"""
        SELECT
        id as id,
        chat_id as chat_id,
        first_name as first_name,
        last_name as last_name,
        username as username,
        active as active,
        register as register
        FROM
        bot_users
        WHERE
        chat_id = {self._db.paramstyle}
        LIMIT 1
        """
        row = await self._db.fetchone(query, (chat_id,), as_dict=True)
        if row is not None:
            return User.parse_obj(row)

    async def create_user(self, new_user: User) -> None:
        query = f"""
        INSERT INTO bot_users (chat_id, first_name, last_name, username, active, register)
        VALUES
        ({self._paramstyle}, {self._paramstyle}, {self._paramstyle}, {self._paramstyle},
        true, datetime('now'))
        ON CONFLICT (chat_id) DO UPDATE SET active = true
        """
        await self._db.execute(
            query,
            (new_user.chat_id, new_user.first_name, new_user.last_name, new_user.username),
        )

    async def activate_user(self, chat_id: int) -> None:
        query = f"""
        UPDATE bot_users
        SET active = {self._paramstyle}
        WHERE chat_id = {self._paramstyle}
        """
        await self._db.execute(
            query,
            (
                True,
                chat_id,
            ),
        )

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        query = """
        SELECT id, chat_id, first_name, last_name, username, active, register
        FROM bot_users
        WHERE bot_users.active = True
        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[User, ...], rows)

    async def get_new_request_token(self) -> Optional[List[Dict[str, str]]]:
        query = """
        SELECT
            request_token as pocket_request_token,
            user_id as user_id
        FROM bot_pocket_integration
        WHERE
        active is TRUE
        AND access_token is NULL
        """
        return await self._db.fetchall(query, as_dict=True)  # type: ignore

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        query = f"""
        SELECT
            request_token as pocket_request_token,
            access_token as pocket_access_token
        FROM bot_pocket_integration bpi
        JOIN bot_users bu on bu.id = bpi.user_id AND chat_id = {self._paramstyle}
        WHERE bpi.active is TRUE
        """
        row = await self._db.fetchone(query, (chat_id,), as_dict=True)
        if row is not None:
            return parse_obj_as(UserIntegration, row)

    async def get_entry_url(self, entry_id: int) -> Optional[str]:
        query = f"""
        SELECT url_article
        FROM bot_article
        WHERE id = {self._paramstyle}
        """
        row = await self._db.fetchone(query, (entry_id,))
        if row:
            return row[0]  # type: ignore

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
        active = FALSE
        WHERE
        user_id = {self._paramstyle}
        """
        await self._db.execute(query, (error_code, error_message, status_code, user_id))
