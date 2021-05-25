from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import aiosqlite


DictAny = Dict[str, Any]
TupleAny = Tuple[Any, ...]
ListDict = List[DictAny]
ListTuple = List[TupleAny]


class Database:
    def __init__(self, url: str):
        self._db = aiosqlite.connect(url)

    async def __aenter__(self) -> "Database":
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()

    @staticmethod
    def _dict_factory(cursor, row) -> Dict:
        """Делаем словарь из ответа базы {"поле": "значение"}"""
        data = {}
        for column, value in zip(cursor.description, row):
            data[column[0]] = value
        return data

    async def connect(self) -> "Database":
        await self._db
        return self

    async def disconnect(self):
        await self._db.close()

    async def fetchall(
        self,
        query: str,
        values: Optional[Iterable[Any]] = None,
        as_dict: bool = False,
    ) -> Optional[Union[DictAny, TupleAny]]:
        self._db.row_factory = self._dict_factory if as_dict else None
        try:
            return await self._db.execute_fetchall(query, values) or None
        finally:
            self._db.row_factory = None

    async def fetchone(
        self,
        query: str,
        values: Optional[Iterable[Any]] = None,
        as_dict: bool = False,
    ) -> Optional[Union[DictAny, Tuple[Any]]]:
        self._db.row_factory = self._dict_factory if as_dict else None
        try:
            cursor = await self._db.execute(query, values)
            row = await cursor.fetchone()
            await cursor.close()
            return row or None
        finally:
            self._db.row_factory = None

    async def execute(
        self, query: str, values: Optional[Iterable[Any]] = None, autocommit: bool = True
    ) -> None:
        await self._db.execute(query, values)
        if autocommit:
            await self._db.commit()

    async def executemany(
        self,
        query,
        values: Iterable[Iterable[Any]],
        autocommit: bool = True,
    ) -> None:
        await self._db.executemany(query, values)
        if autocommit:
            await self._db.commit()
