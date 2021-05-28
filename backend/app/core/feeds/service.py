from app.core.feeds.repository import FeedsRepository


class FeedsService:
    def __init__(self, repository: FeedsRepository):
        self._repository = repository
