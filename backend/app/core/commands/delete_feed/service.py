from typing import Tuple

from loguru import logger

from app.api.endpoints.update.enums import ParseMode
from app.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.feeds.models import Feed
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService
from app.core.utils import validate_url
from app.reporters_errors import get_telegram_reporter


telegram_reporter = get_telegram_reporter()


class CommandDeleteFeedService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        internal_messages_service: InternalMessagesService,
    ):
        self._feeds_service = feeds_service
        self._telegram = telegram
        self.internal_messages_service = internal_messages_service

    @staticmethod
    def _format_deleted_list_msg(active_feeds: Tuple[Feed, ...]) -> str:
        title = "For unsubscribe send:\n"
        return title + "\n".join(f"`/delete_feed {feed.url}`\n" for feed in active_feeds)

    @telegram_reporter(as_attached=True)
    async def handle(self, update: Update) -> None:
        user_input = update.text.replace("/delete_feed", "", 1).strip().split()

        if not user_input:
            logger.debug("Пришел запрос на получение списка фидов для удаления.")
            active_feeds = await self._feeds_service.get_active_feeds(update.chat_id)

            if active_feeds is None:
                logger.debug("У пользователя нет активных фидов.")
                await self.internal_messages_service.send(
                    update.chat_id,
                    InternalMessages.not_have_active,
                )
                return

            text = self._format_deleted_list_msg(active_feeds)
            await self._telegram.send_message(update.chat_id, text, parse_mode=ParseMode.MarkdownV2)

        else:
            url_feed = user_input[0]
            logger.debug("Пришел запрос на удаление фида. url={}", url_feed)

            if not validate_url(url_feed):
                logger.warning("Некорректный url. {}", url_feed)
                await self.internal_messages_service.send(
                    update.chat_id,
                    InternalMessages.incorrect_rss,
                )
                return

            exists_feed = await self._feeds_service.exists_active_feed_user(
                update.chat_id,
                url_feed,
            )
            if not exists_feed:
                logger.warning("Попытка удалить фид, который не добавлен. {}", url_feed)
                await self.internal_messages_service.send(
                    update.chat_id,
                    InternalMessages.url_not_founded,
                )
                return

            logger.debug("Удаление фида {} ...", url_feed)
            await self._feeds_service.disable_feed(url_feed, update.chat_id)
            text = f"{url_feed} has been removed from your feed."
            await self._telegram.send_message(update.chat_id, text, disable_web_page_preview=True)
