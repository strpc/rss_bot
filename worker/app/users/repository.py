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

    async def get_user_integration(self, chat_id: int) -> Optional[UserIntegration]:
        query = f"""
        SELECT
            request_token as pocket_request_token,
            access_token as pocket_access_token,
            chat_id
        FROM bot_pocket_integration bpi
        JOIN bot_users bu on bu.id = bpi.user_id AND chat_id = {self._paramstyle}
        WHERE bpi.active is TRUE
        """
        row = await self._db.fetchone(query, (chat_id,), as_dict=True)
        if row is not None:
            return parse_obj_as(UserIntegration, row)
