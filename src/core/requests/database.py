from abc import ABC
from typing import Dict, List
import sqlite3
import logging

from src.project.settings import DB_PATH


logger = logging.getLogger(__name__)


class Client(ABC):

    @staticmethod
    def dict_factory(cursor, row) -> Dict:
        """Делаем словарь из ответа базы {"поле": "значение"}"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __enter__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = self.dict_factory
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def fetchall(self, query: str) -> List[Dict]:
        try:
            with self as database:
                database.execute(query)
                return database.fetchall()

        except Exception as error:
            logger.error(error)
            logger.info(query)

    def execute(self, query: str) -> bool:
        try:
            with self as database:
                database.execute(query)
            return True

        except Exception as error:
            logger.error(error)
            logger.info(query)
            return False


class Database(Client):
    def __init__(self):
        pass


