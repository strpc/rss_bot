from abc import ABC, abstractmethod


class ExternalService(ABC):
    @abstractmethod
    async def send(self, chat_id: int, url: str) -> None:
        ...
