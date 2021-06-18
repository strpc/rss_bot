from typing import Optional

from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.integration.exceptions import SendingError
from app.core.integration.integration_abc import ExternalServiceABC
from app.core.integration.service import ExternalServices
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.core.users.service import UsersService
from app.schemas.callback import Callback
from app.schemas.enums import ServiceIntegration
from app.schemas.message import Button


class CallbackService(CommandServiceABC):
    def __init__(
        self,
        *,
        users_service: UsersService,
        external_services: ExternalServices,
        service_messages: ServiceMessagesService,
        telegram: Telegram,
    ):
        self._services = external_services
        self._users_service = users_service
        self._service_messages = service_messages
        self._telegram = telegram

    def _get_service(self, name: ServiceIntegration) -> ExternalServiceABC:
        return self._services.get_service(name)

    async def _get_entry_url(self, entry_id: int) -> Optional[str]:
        return await self._users_service.get_entry_url(entry_id)

    async def handle(self, update: Callback) -> None:
        if update.callback_query.data.sended:  # type: ignore
            logger.info("Повторный клик на кнопку.")
            return

        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        payload = update.callback_query.data
        logger.info("payload={}", payload)

        service = self._get_service(payload.service)  # type: ignore

        url = await self._get_entry_url(payload.entry_id)  # type: ignore
        if url is None:
            await self._service_messages.send(chat_id, ServiceMessage.error)

        try:
            await service.send(
                chat_id=chat_id,
                url=url,  # type: ignore
            )
            new_button_text = service.get_update_message()
        except SendingError:
            new_button_text = service.get_error_message()

        new_buttons = []
        for button in update.callback_query.message.reply_markup.inline_keyboard[0]:
            if button.callback_data.service == payload.service:  # type: ignore
                button.text = new_button_text
                button.callback_data.sended = True
                button.callback_data = button.callback_data.json()

            new_buttons.append(Button(**button.dict()))

        await self._telegram.update_buttons(
            chat_id=chat_id,
            message_id=message_id,
            inline_keyboard=new_buttons,
        )
