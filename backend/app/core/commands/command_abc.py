from abc import ABC, abstractmethod

from app.schemas.message import Message


class Command(ABC):
    @abstractmethod
    async def handle(self, update: Message, repository) -> None:  # type: ignore  # FIXME PLEASE
        pass
