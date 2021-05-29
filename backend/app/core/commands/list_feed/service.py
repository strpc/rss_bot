from typing import Tuple

from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandListFeedService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._telegram = telegram
        self._feeds_service = feeds_service
        self._service_messages = service_messages

    @staticmethod
    def _format_subscribed_msg(list_feeds: Tuple[str, ...]) -> str:
        return "You are subscribed to:\n{}".format("\n".join(list_feeds))

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        active_feeds = await self._feeds_service.get_active_feeds(chat_id)

        if active_feeds is None:
            logger.debug("У пользователя нет активных фидов.")
            await self._service_messages.send(chat_id, ServiceMessage.not_have_active)
            return

        text = self._format_subscribed_msg(active_feeds)
        await self._telegram.send_message(chat_id, text, disable_web_page_preview=True)
