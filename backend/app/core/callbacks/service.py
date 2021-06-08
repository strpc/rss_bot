from app.core.commands.command_abc import CommandServiceABC
from app.schemas.callback import Callback


class CallbackService(CommandServiceABC):
    async def handle(self, update: Callback) -> None:
        print("hello world")
