from urllib.parse import urlparse

from loguru import logger

from app.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.commands.dto import Update
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import InternalMessages
from app.core.service_messages.service import InternalMessagesService
from app.core.utils import validate_url
from app.reporters_errors import get_telegram_reporter


telegram_reporter = get_telegram_reporter()


class CommandAddFeedService(CommandServiceABC):
    def __init__(
        self,
        *,
        feeds_service: FeedsService,
        telegram: Telegram,
        internal_messages_service: InternalMessagesService,
        limit_feed: int,
    ):
        self._telegram = telegram
        self._feeds_service = feeds_service
        self._internal_messages_service = internal_messages_service
        self._limit_feed = limit_feed

    @staticmethod
    def _strip_scheme(url: str) -> str:
        parsed_url = urlparse(url)
        scheme = f"{parsed_url.scheme}://"
        return url.replace(scheme, "", 1)

    async def _exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        return await self._feeds_service.exists_active_feed_user(chat_id=chat_id, url=url)

    async def _is_feed(self, url: str) -> bool:
        return await self._feeds_service.validate_feed(url)

    async def _achieved_limit_feeds(self, chat_id: int) -> bool:
        active_feeds = await self._feeds_service.get_active_feeds(chat_id)
        if active_feeds is not None:
            return len(active_feeds) >= self._limit_feed
        return False

    @telegram_reporter(as_attached=True)
    async def handle(self, update: Update) -> None:
        url = update.text.replace("/add_feed", "", 1).strip().split()

        if not url or not validate_url(url[0]):
            logger.warning("Некорректный url. {}", url)
            await self._internal_messages_service.send(
                update.chat_id,
                InternalMessages.incorrect_rss,
            )
            return

        url_without_schema = self._strip_scheme(url[0])
        if not await self._is_feed(url[0]):
            logger.warning("URL не является фидом. url={}", url[0])
            await self._internal_messages_service.send(
                update.chat_id,
                InternalMessages.incorrect_rss,
            )
            return

        if await self._exists_active_feed_user(update.chat_id, url_without_schema):
            logger.warning("Попытка добавить один и тот же фид дважды. url={}", url[0])
            await self._internal_messages_service.send(
                update.chat_id,
                InternalMessages.already_added_feed,
            )
            return

        if await self._achieved_limit_feeds(update.chat_id):
            logger.warning("Достигнут предел кол-во фидов.")
            await self._internal_messages_service.send(
                update.chat_id,
                InternalMessages.limit_achieved,
            )
            return

        logger.debug("Новый feed. {}", url[0])
        await self._feeds_service.add_new_feed_user(update.chat_id, url[0])
        text = f"{url[0]} was added."
        await self._telegram.send_message(update.chat_id, text, disable_web_page_preview=True)
