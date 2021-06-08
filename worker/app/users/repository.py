import itertools
from typing import Optional, Tuple

from pydantic import parse_obj_as

from app.clients.database import Database
from app.users.models import User, UserIntegration


class UsersRepository:
    def __init__(self, db: Database):
        self._db = db
        self._paramstyle = db.paramstyle

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        query = """
        SELECT id, chat_id, first_name, last_name, username, active, register
        FROM bot_users
        WHERE bot_users.active = True
        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[User, ...], rows)

    async def get_new_request_token(self) -> Optional[Tuple[str, ...]]:
        query = """
        SELECT
            request_token as pocket_request_token
        FROM bot_pocket_integration
        WHERE
        active is TRUE
        AND access_token is NULL
        """
        rows = await self._db.fetchall(query)
        if rows is not None:
            return tuple(itertools.chain.from_iterable(rows))

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

    async def update_pocket_meta(
        self,
        request_token: str,
        access_token: str,
        username: str,
    ) -> None:
        query = f"""
        UPDATE bot_pocket_integration
        SET
        access_token = {self._paramstyle},
        username = {self._paramstyle}
        WHERE
        request_token = {self._paramstyle}
        """
        await self._db.execute(query, (access_token, username, request_token))
