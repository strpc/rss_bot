from typing import Optional
from urllib.parse import ParseResult as ParsedUrl
from urllib.parse import urlparse

from loguru import logger

from app.core.clients.telegram import Telegram
from app.core.feeds.service import FeedsService
from app.core.service_messages.models import ServiceMessage
from app.core.service_messages.service import ServiceMessagesService
from app.schemas.message import Message


class CommandAddFeedService:
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
    def _strip_scheme(url: ParsedUrl) -> str:
        logger.debug("Уберем схему из url={}...", url)
        scheme = f"{url.scheme}://"
        return url.geturl().replace(scheme, "", 1)

    @staticmethod
    def _validate_url(url: str) -> Optional[ParsedUrl]:
        logger.debug("Провалидируем url {} ...", url)
        parsed_url = urlparse(url)
        if all([parsed_url.scheme, parsed_url.netloc, parsed_url.path]):
            logger.debug("URL={} валиден. {}", url, parsed_url)
            return parsed_url
        return None

    async def _exists_active_feed_user(self, chat_id: int, url: str) -> bool:
        return await self._feeds_service.exists_active_feed_user(chat_id=chat_id, url=url)

    async def _is_feed(self, url: str) -> bool:
        return await self._feeds_service.validate_feed(url)

    async def handle(self, update: Message) -> None:
        chat_id = update.message.chat.id
        url = update.message.text.replace("/add_feed", "", 1).strip()
        validated_url = self._validate_url(url)

        if validated_url is None:
            logger.warning("Некорректный url. {}", url)
            await self._service_messages.send(chat_id, ServiceMessage.incorrect_rss)
            return

        url_without_schema = self._strip_scheme(validated_url)
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
        await self._telegram.send_message(chat_id, text)
        return
