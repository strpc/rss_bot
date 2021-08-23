from abc import ABC, abstractmethod

from app.api.schemas.message import Message


class CommandServiceABC(ABC):
    @abstractmethod
    async def handle(self, update: Message) -> None:
        pass
