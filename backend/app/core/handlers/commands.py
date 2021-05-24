import logging
import random

from app.core.clients import ITelegram
from app.core.db import IDatabase
from app.core.schemas.rss import Feed, ListFeeds
from app.core.utils import get_hash, make_str_urls
from app.project.settings import COUNT_FEED_FOR_ADD, PARSE_MODE_MARKDOWN
from pydantic import ValidationError

from app.core import schemas


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
        message = self._db.get_service_message("hello_user")["text"]
        self._telegram.send_message(chat_id=update.message.chat.id, text=message)

    def add_feed(self, update: schemas.Message):
        # todo: добавить ограничение на кол-во записей зараз. из конфига
        logger.debug("/add_feed enter...")
        list_urls = ListFeeds(feeds=update.message.text)
        chat_id = update.message.chat.id

        for url in list_urls[:COUNT_FEED_FOR_ADD]:
            logger.debug("Process url=%s...", url)
            hash_url = get_hash(url, update.message.chat.id)
            self._db.add_feed(url=str(url), chat_id=chat_id, hash_url=hash_url)
            logger.info("Добавлен новый фид url=%s chat_id=%s", url, chat_id)

        if len(list_urls) > 1:
            text = f"URLs: {make_str_urls(list_urls)} \nhas beed added to your feed."
        elif len(list_urls) == 1:
            text = f"URL: {make_str_urls(list_urls)} \nhas beed added to your feed."
        else:
            text = self._db.get_service_message("incorrect_rss")["text"]

        self._telegram.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)

    def list_feed(self, update: schemas.Message):
        chat_id = update.message.chat.id

        list_dicts_urls = self._db.list_feed(chat_id)

        if list_dicts_urls is None:
            msg = self._db.get_service_message("not_have_active")["text"]
        else:
            list_str_urls = [url.get("url") for url in list_dicts_urls]
            msg = f"You are subscribed to:\n{make_str_urls(list_str_urls)}"

        self._telegram.send_message(chat_id=chat_id, text=msg, disable_web_page_preview=True)

    def delete_feed(self, update: schemas.Message):
        chat_id = update.message.chat.id
        user_input = update.message.text.replace("/delete_feed", "")

        if not user_input:
            list_dicts_urls = self._db.list_feed(chat_id)

            text = "For unsubscribe send:\n"
            while list_dicts_urls:
                url = list_dicts_urls.pop(random.randint(0, len(list_dicts_urls) - 1))
                text += f"`/delete_feed {url['url']}`\n"

            self._telegram.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=PARSE_MODE_MARKDOWN,
                disable_web_page_preview=True,
            )
        else:
            try:
                url = Feed(url=user_input)
            except ValidationError:
                msg = self._db.get_service_message("incorrect_rss")["text"]
                self._telegram.send_message(chat_id=chat_id, text=msg)
                return

            if self._db.delete_feed(url.url, chat_id):
                self._telegram.send_message(
                    chat_id=chat_id,
                    text=f"URL {url.url} has been removed from your feed",
                    disable_web_page_preview=True,
                )
            else:
                msg = self._db.get_service_message("url_not_founded")["text"]
                self._telegram.send_message(chat_id=chat_id, text=msg)
