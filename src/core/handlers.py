import logging

from src.core.schemas.update import BotCommand
from src.core.utils import list_urls


logger = logging.getLogger(__name__)


class CommandHandler:
    @staticmethod
    def start(message: BotCommand):
        message.init_user()
        if message.new_user:
            message.register_user()
        message.request.send_message('здарова дятел')

    @staticmethod
    def add_feed(message: BotCommand):
        urls = list_urls(message.text.replace('/add_feed', ''))

        pass  # INSERT OR IGNORE

    @staticmethod
    def delete_feed(message: BotCommand):
        pass

    @staticmethod
    def list_feed(message: BotCommand):
        pass
