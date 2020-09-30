from datetime import datetime
import logging
import random
from pprint import pprint

from pydantic import ValidationError

from src.core.schemas.update import BotCommand
from src.core.schemas.rss import ListUrls, UrlFeed
from src.core.utils import make_str_urls, make_hash
from src.project.settings import PARSE_MODE_MARKDOWN


logger = logging.getLogger(__name__)


class CommandHandler:
    @staticmethod
    def start(message: BotCommand):
        message.init_user()
        if message.new_user:
            message.register_user()
            message.request.send_message('здарова дятел')
            # первый старт/рестарт пользователем
        # повторный /start без остановки бота
        message.send_message('hello world')
        print('hello method start')

    @staticmethod
    def add_feed(message: BotCommand):
        list_urls = ListUrls(list_urls=message.text)

        values_for_execute = []
        for url in list_urls:
            values_for_execute.append(
                (str(url), datetime.utcnow(), True, message.chat_id,
                 make_hash(url, message.chat_id))
            )
        message.add_feed(values_for_execute)

        text = 'твои ссылки - шляпа'  # заглушка, если вдруг пришла одна ссылка и она не rss
        if len(list_urls) > 1:
            text = f"URLs: {make_str_urls(list_urls)} \nhas beed added to your feed."
        elif len(list_urls) == 1:
            text = f"URL: {make_str_urls(list_urls)} \nhas beed added to your feed."
        message.send_message(text, disable_web_page_preview=True)

    @staticmethod
    def list_feed(message: BotCommand):
        list_dicts_urls = message.list_feed()
        list_str_urls = [i.get('url') for i in list_dicts_urls]
        msg = f'You are subscribed to:\n{make_str_urls(list_str_urls)}'
        message.send_message(msg, disable_web_page_preview=True)

    @staticmethod
    def delete_feed(message: BotCommand):
        if not message.text:
            list_dicts_urls = message.list_feed()
            text = 'For unsubscribe send:\n'
            for item in range(0, len(list_dicts_urls)):
                url = random.choice(list_dicts_urls)
                text += f"`/delete_feed {url['url']}`\n"
                list_dicts_urls.remove(url)
            message.send_message(text, PARSE_MODE_MARKDOWN, True)
        else:
            try:
                url = UrlFeed(url_feed=message.text)
            except ValidationError:
                message.send_message('Bad url')
                return
            if message.delete_feed(url.url_feed):
                message.send_message(
                    f'URL {url.url_feed} has been removed from your feed',
                    disable_web_page_preview=True
                )
            else:
                message.send_message('такого урла не найдено')
