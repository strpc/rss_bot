import logging
import random

from pydantic import ValidationError

from app.core import schemas
from app.core.clients import ITelegram
from app.core.db import IDatabase
from app.core.schemas.rss import ListUrls, UrlFeed
from app.core.utils import get_hash, make_str_urls
from app.project.settings import PARSE_MODE_MARKDOWN


logger = logging.getLogger(__name__)


class CommandHandler:
    def __init__(self, *, database: IDatabase, telegram: ITelegram):
        self._db = database
        self._telegram = telegram

    def start(self, update: schemas.Message):
        logger.debug("/start enter...")
        if self._db.registered_user(update.message.chat.id) is True:
            logger.warning("Авторизированный юзер: %s", update)
            return

        self._db.register_user(
            chat_id=update.message.chat.id,
            first_name=update.message.user.first_name,
            last_name=update.message.user.last_name,
            username=update.message.user.username,
        )
        logger.debug(
            "Пользователь username=%s, chat_id=%s зарегестрирован",
            update.message.user.username,
            update.message.chat.id,
        )
        message = self._db.get_service_message("hello_user")
        self._telegram.send_message(chat_id=update.message.chat.id, text=message["text"])

    def add_feed(self, update: schemas.Message):
        # todo: добавить ограничение на кол-во записей зараз. из конфига
        logger.debug("/add_feed enter...")
        list_urls = ListUrls.get_instance(update.message.text)
        chat_id = update.message.chat.id

        for url in list_urls:
            logger.debug("Process url=%s...", url)
            hash_url = get_hash(url, update.message.chat.id)
            self._db.add_feed(url=url, chat_id=chat_id, hash_url=hash_url)
            logger.info("Добавлен новый фид url=%s chat_id=%s", url, chat_id)

        if len(list_urls) > 1:
            text = f"URLs: {make_str_urls(list_urls)} \nhas beed added to your feed."
        elif len(list_urls) == 1:
            text = f"URL: {make_str_urls(list_urls)} \nhas beed added to your feed."
        else:
            text = "твои ссылки - шляпа"  # заглушка, если вдруг пришла одна ссылка и она не rss
        self._telegram.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)

    @staticmethod
    def list_feed(message):
        list_dicts_urls = message.list_feed(message.chat_id)
        if list_dicts_urls is None:
            msg = "You not have active subscriptions."
        else:
            list_str_urls = [i.get("url") for i in list_dicts_urls]
            msg = f"You are subscribed to:\n{make_str_urls(list_str_urls)}"
        message.send_message(msg, disable_web_page_preview=True)

    @staticmethod
    def delete_feed(message):
        if not message.text:
            list_dicts_urls = message.list_feed(message.chat_id)
            text = "For unsubscribe send:\n"
            for item in range(0, len(list_dicts_urls)):
                url = random.choice(list_dicts_urls)
                text += f"`/delete_feed {url['url']}`\n"
                list_dicts_urls.remove(url)
            message.send_message(text, PARSE_MODE_MARKDOWN, True)
        else:
            try:
                url = UrlFeed(url_feed=message.text)
            except ValidationError:
                message.send_message("Bad url")
                return
            if message.delete_feed(url.url_feed, message.chat_id):
                message.send_message(
                    f"URL {url.url_feed} has been removed from your feed",
                    disable_web_page_preview=True,
                )
            else:
                message.send_message("такого урла не найдено")
