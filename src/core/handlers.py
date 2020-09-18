import logging
from pprint import pprint

from src.core.schemas.update import BotCommand
from src.core.schemas.rss import ListUrls


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
        # todo: сделать валидацию урлов
        message.database.add_feed(list_urls)
        # INSERT OR IGNORE

    @staticmethod
    def delete_feed(message: BotCommand):
        pass

    @staticmethod
    def list_feed(message: BotCommand):
        pass


# {
#   "ok": false,
#   "error_code": 403,
#   "description": "Forbidden: bot was blocked by the user"
# }
