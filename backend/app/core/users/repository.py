from typing import Optional

from pydantic import parse_obj_as

from app.clients.database import Database
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
            is_blocked as is_blocked,
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

    async def create_user(self, new_user: User) -> int:
        query = f"""
        INSERT INTO bot_users
            (chat_id, first_name, last_name, username, active, is_blocked, register)
        VALUES
            ({self._paramstyle}, {self._paramstyle}, {self._paramstyle}, {self._paramstyle},
            true, false, datetime('now'))
        ON CONFLICT (chat_id) DO UPDATE SET active = true
        """
        return await self._db.insert_one(
            query,
            (new_user.chat_id, new_user.first_name, new_user.last_name, new_user.username),
        )

    async def disable_user(self, chat_id: int) -> None:
        query = f"""
        UPDATE bot_users
        SET
            active = false
        WHERE
            chat_id = {self._paramstyle}
        """
        await self._db.execute(query, (chat_id,))

    async def activate_user(self, chat_id: int) -> None:
        query = f"""
        UPDATE bot_users
        SET
            active = {self._paramstyle}
        WHERE
            chat_id = {self._paramstyle}
        """
        await self._db.execute(
            query,
            (
                True,
                chat_id,
            ),
        )

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
