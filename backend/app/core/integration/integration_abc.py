from abc import ABC, abstractmethod


class ExternalServiceABC(ABC):
    @abstractmethod
    async def send(self, *, chat_id: int, url: str) -> None:
        ...

    @abstractmethod
    def get_update_message(self) -> str:
        ...

    @abstractmethod
    def get_error_message(self) -> str:
        ...
