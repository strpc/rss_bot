from app.core.clients.database import Database


class CommandDeleteFeedRepository:
    def __init__(self, database: Database):
        self._db = database
