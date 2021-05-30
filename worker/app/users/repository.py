from typing import Optional, Tuple

from pydantic import parse_obj_as

from app.clients.database import Database
from app.users.models import User


class UsersRepository:
    def __init__(self, db: Database):
        self._db = db

    async def get_active_users(self) -> Optional[Tuple[User, ...]]:
        query = """
        SELECT id, chat_id, first_name, last_name, username, active, register
        FROM bot_users
        WHERE bot_users.active = True
        """
        rows = await self._db.fetchall(query, as_dict=True)
        if rows is not None:
            return parse_obj_as(Tuple[User, ...], rows)
