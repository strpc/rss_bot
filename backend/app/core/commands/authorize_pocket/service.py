from app.core.clients.pocket import PocketClient
from app.core.clients.telegram import Telegram
from app.core.commands.authorize_pocket.repository import PocketAuthRepository
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService


class AuthorizePocketService(CommandServiceABC):
    def __init__(
        self,
        *,
        telegram: Telegram,
        pocket_client: PocketClient,
        repository: PocketAuthRepository,
        internal_messages_service: InternalMessagesService,
    ):
        self._telegram = telegram
        self._internal_messages_service = internal_messages_service
        self._pocket_client = pocket_client
        self._repository = repository

    async def authorize(self, update: Update) -> None:
        request_token = await self._pocket_client.get_request_token()
        if request_token is None:
            await self._internal_messages_service.send(update.chat_id, InternalMessages.error)
            return

        await self._repository.save_request_token(update.chat_id, request_token)
        text = await self._pocket_client.get_auth_url(request_token)
        await self._telegram.send_message(
            update.chat_id,
            f"Authorize Pocket:\n{text}",
            disable_web_page_preview=True,
        )

    async def unauthorize(self, update: Update) -> None:
        request_token = await self._repository.get_request_token(update.chat_id)
        if request_token is None:
            await self._internal_messages_service.send(update.chat_id, InternalMessages.error)
            return

        await self._repository.disable_pocket_integration(update.chat_id)
        await self._internal_messages_service.send(
            update.chat_id,
            InternalMessages.unauthorize_pocket,
        )

    async def handle(self, update: Update) -> None:
        commands_handlers_map = {
            "authorize_pocket": self.authorize,
            "unauthorize_pocket": self.unauthorize,
        }
        return await commands_handlers_map[update.command](update)  # type: ignore
