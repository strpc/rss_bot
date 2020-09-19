import logging
from pprint import pprint
from random import choice

from pydantic import ValidationError

from src.core.schemas.update import BotCommand
from src.core.schemas.rss import ListUrls, UrlFeed
from src.core.utils import make_str_urls
from src.project.settings import parse_mode_markdown


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
        print('hello method start')

    @staticmethod
    def add_feed(message: BotCommand):
        list_urls = ListUrls(list_urls=message.text)
        message.add_feed(list_urls)

        message.send_message(f"URLs: {make_str_urls(list_urls)} \n has "
                             f"beed added to your feed.")

    @staticmethod
    def list_feed(message: BotCommand):
        list_dicts_urls = message.list_feed()
        list_str_urls = [i.get('url') for i in list_dicts_urls]
        msg = f'You are subscribed to:\n{make_str_urls(list_str_urls)}'
        message.send_message(msg)

    @staticmethod
    def delete_feed(message: BotCommand):
        if not message.text:
            list_dicts_urls = message.list_feed()
            text = 'For unsubscribe send:\n'
            for item in range(0, len(list_dicts_urls)):
                url = choice(list_dicts_urls)
                text += f"`/delete_feed {url['url']}`\n"
                list_dicts_urls.remove(url)
            message.send_message(text, parse_mode_markdown, True)
        else:
            try:
                url = UrlFeed(url_feed=message.text)
            except ValidationError:
                message.send_message('Bad url')
                return
            if message.delete_feed(str(url)):
                message.send_message(
                    f'URL {str(url)} has been removed from your feed', disable_web_page_preview=True
                )




# {
#   "ok": false,
#   "error_code": 403,
#   "description": "Forbidden: bot was blocked by the user"
# }
