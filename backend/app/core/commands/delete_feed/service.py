from typing import Tuple

from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.feeds.models import Feed
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.core.utils import validate_url
from app.schemas.enums import ParseMode
from app.schemas.message import Message


class CommandDeleteFeedService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        service_messages: ServiceMessagesService,
    ):
        self._feeds_service = feeds_service
        self._telegram = telegram
        self._service_messages = service_messages

    @staticmethod
    def _format_deleted_list_msg(active_feeds: Tuple[Feed, ...]) -> str:
        text = "For unsubscribe send:\n"
        for feed in active_feeds:
            text += f"`/delete_feed {feed.url}`\n"
        return text

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        user_input = update.message.text.replace("/delete_feed", "", 1).strip().split()

        if not user_input:
            logger.debug("Пришел запрос на получение списка фидов для удаления.")
            active_feeds = await self._feeds_service.get_active_feeds(chat_id)

            if active_feeds is None:
                logger.debug("У пользователя нет активных фидов.")
                await self._service_messages.send(chat_id, ServiceMessage.not_have_active)
                return

            text = self._format_deleted_list_msg(active_feeds)
            await self._telegram.send_message(chat_id, text, parse_mode=ParseMode.MarkdownV2)

        else:
            url_feed = user_input[0]
            logger.debug("Пришел запрос на удаление фида. url={}", url_feed)

            if not validate_url(url_feed):
                logger.warning("Некорректный url. {}", url_feed)
                await self._service_messages.send(chat_id, ServiceMessage.incorrect_rss)
                return

            exists_feed = await self._feeds_service.exists_active_feed_user(chat_id, url_feed)
            if not exists_feed:
                logger.warning("Попытка удалить фид, который не добавлен. {}", url_feed)
                await self._service_messages.send(chat_id, ServiceMessage.url_not_founded)
                return

            logger.debug("Удаление фида {} ...", url_feed)
            await self._feeds_service.disable_feed(url_feed, chat_id)
            text = f"{url_feed} has been removed from your feed."
            await self._telegram.send_message(chat_id, text, disable_web_page_preview=True)
