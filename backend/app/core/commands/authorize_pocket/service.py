from app.core.clients.pocket import PocketClient
from app.core.clients.telegram import Telegram
from app.core.commands.authorize_pocket.repository import PocketAuthRepository
from app.core.commands.command_abc import CommandServiceABC
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class AuthorizePocketService(CommandServiceABC):
    def __init__(
        self,
        *,
        telegram: Telegram,
        pocket_client: PocketClient,
        repository: PocketAuthRepository,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._service_messages = service_messages
        self._pocket_client = pocket_client
        self._repository = repository

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        request_token = await self._pocket_client.get_request_token()
        if request_token is None:
            await self._service_messages.send(chat_id, ServiceMessage.error)
            return

        # await self._repository.save_request_token(chat_id, request_token)
        text = await self._pocket_client.get_auth_url(request_token)
        await self._telegram.send_message(chat_id, text, disable_web_page_preview=True)
