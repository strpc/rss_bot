from abc import ABC, abstractmethod


class ExternalServiceABC(ABC):
    @abstractmethod
    async def send(self, *, chat_id: int, url: str) -> None:
        ...

    @staticmethod
    @abstractmethod
    def get_update_message() -> str:
        ...
