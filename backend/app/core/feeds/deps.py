from fastapi import Depends

from app.core.base_deps import get_database
from app.core.clients.database import Database
from app.core.feeds.repository import FeedsRepository
from app.core.feeds.service import FeedsService


def get_feeds_repository(database: Database = Depends(get_database)) -> FeedsRepository:
    return FeedsRepository(database=database)


def get_feeds_service(repository: FeedsRepository = Depends(get_feeds_repository)) -> FeedsService:
    return FeedsService(repository=repository)
