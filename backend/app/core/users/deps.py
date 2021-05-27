from fastapi import Depends

from app.core.base_deps import get_database
from app.core.clients.database import Database
from app.core.users.repository import UsersRepository
from app.core.users.service import UsersService


def get_users_repository(db: Database = Depends(get_database)) -> UsersRepository:
    return UsersRepository(database=db)


def get_users_service(
    users_repository: UsersRepository = Depends(get_users_repository),
) -> UsersService:
    return UsersService(repository=users_repository)
