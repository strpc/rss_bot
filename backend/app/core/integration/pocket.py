from app.core.integration.integration_abc import ExternalService


class PocketIntegration(ExternalService):
    def __init__(self):  # type: ignore
        pass

    async def send(self, chat_id: int, url: str) -> None:
        pass
