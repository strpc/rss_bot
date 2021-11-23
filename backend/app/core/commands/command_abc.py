from abc import ABC, abstractmethod

from app.core.commands.dto import Update


class CommandServiceABC(ABC):
    @abstractmethod
    async def handle(self, update: Update) -> None:
        pass
