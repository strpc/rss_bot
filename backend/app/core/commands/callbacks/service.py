from typing import Optional

from loguru import logger

from app.api.endpoints.update.enums import ServiceIntegration

# from app.api.endpoints.update.schemas import Button
from app.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.feeds.service import FeedsService
from app.core.integration.exceptions import SendingError
from app.core.integration.integration_abc import ExternalServiceABC
from app.core.integration.service import ExternalServices
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService


class CallbackService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        external_services: ExternalServices,
        internal_messages_service: InternalMessagesService,
        telegram: Telegram,
    ):
        self._services = external_services
        self._feeds_service = feeds_service
        self._internal_messages_service = internal_messages_service
        self._telegram = telegram

    def _get_service(self, name: ServiceIntegration) -> ExternalServiceABC:
        return self._services.get_service(name)

    async def _get_entry_url(self, entry_id: int) -> Optional[str]:
        return await self._feeds_service.get_entry_url(entry_id)

    async def handle(self, update: Update) -> None:
        if update.callback_query.data.sended:  # type: ignore
            logger.info("Повторный клик на кнопку.")
            return

        logger.debug("payload={}", update.payload)
        await self._telegram.answer_callback(update.callback_query.id, "Saving...")  # type: ignore

        service = self._get_service(update.payload.service)  # type: ignore

        url = await self._get_entry_url(update.payload.entry_id)  # type: ignore
        if url is None:
            await self._internal_messages_service.send(update.chat_id, InternalMessages.error)
            return

        try:
            await service.send(
                chat_id=update.chat_id,
                url=url,  # type: ignore
            )
            new_button_text = service.get_update_message()
        except SendingError:
            new_button_text = service.get_error_message()

        new_buttons = []
        for button in update.callback_query.message.reply_markup.inline_keyboard[0]:  # type: ignore
            if button.callback_data.service == update.payload.service:  # type: ignore
                button.text = new_button_text
                button.callback_data.sended = True
                button.callback_data = button.callback_data.json()

            # new_buttons.append(Button(**button.dict()))
            new_buttons.append(button)

        await self._telegram.update_buttons(
            chat_id=update.chat_id,
            message_id=update.message_id,  # type: ignore
            inline_keyboard=new_buttons,
        )
