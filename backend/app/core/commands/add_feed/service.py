from urllib.parse import urlparse

from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.commands.command_abc import CommandServiceABC
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.core.utils import validate_url
from app.schemas.message import Message


class CommandAddFeedService(CommandServiceABC):
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
    def _strip_scheme(url: str) -> str:
        logger.debug("Уберем схему из url={}...", url)
        parsed_url = urlparse(url)
        scheme = f"{parsed_url.scheme}://"
        return url.replace(scheme, "", 1)

    async def _exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        return await self._feeds_service.exists_active_feed_user(chat_id=chat_id, url=url)

    async def _is_feed(self, url: str) -> bool:
        return await self._feeds_service.validate_feed(url)

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        url = update.message.text.replace("/add_feed", "", 1).strip().split()[0]

        if not validate_url(url):
            logger.warning("Некорректный url. {}", url)
            await self._service_messages.send(chat_id, ServiceMessage.incorrect_rss)
            return

        url_without_schema = self._strip_scheme(url)
        if not await self._is_feed(url):
            logger.warning("URL не является фидом. url={}", url)
            await self._service_messages.send(chat_id, ServiceMessage.incorrect_rss)
            return

        if await self._exists_active_feed_user(chat_id, url_without_schema):
            logger.warning("Попытка добавить один и тот же фид дважды. url={}", url)
            await self._service_messages.send(chat_id, ServiceMessage.already_added_feed)
            return

        logger.debug("Новый feed. {}", url)
        await self._feeds_service.add_feed(url, chat_id)
        text = f"{url} was added."
        await self._telegram.send_message(chat_id, text, disable_web_page_preview=True)
        return
