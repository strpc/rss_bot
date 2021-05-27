from app.core.clients.database import Database


class CommandStartRepository:
    def __init__(self, database: Database):
        self._db = database
