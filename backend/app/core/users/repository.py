from typing import Optional

from app.core.clients.database import Database
from app.core.users.models import User


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
        chat_id = {self._paramstyle}
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
