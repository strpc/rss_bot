from typing import Tuple

from loguru import logger

from app.api.schemas.message import Message
from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.feeds.models import Feed
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService


class CommandListFeedService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        internal_messages_service: InternalMessagesService,
    ):
        self._telegram = telegram
        self._feeds_service = feeds_service
        self._internal_messages_service = internal_messages_service

    @staticmethod
    def _format_subscribed_msg(list_feeds: Tuple[Feed, ...]) -> str:
        nl = "\n"
        return f"You are subscribed to:{nl}{nl.join(feed.url for feed in list_feeds)}"

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        active_feeds = await self._feeds_service.get_active_feeds(chat_id)

        if active_feeds is None:
            logger.debug("У пользователя нет активных фидов.")
            await self._internal_messages_service.send(chat_id, InternalMessages.not_have_active)
            return

        text = self._format_subscribed_msg(active_feeds)
        await self._telegram.send_message(chat_id, text, disable_web_page_preview=True)
