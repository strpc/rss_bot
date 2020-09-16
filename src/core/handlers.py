from src.core.models.update import BaseMessage


def start_bot(message: BaseMessage):
    pass


def add_feed(message: BaseMessage):
    pass


handlers_command = {
    '/start': start_bot,
    '/addfeed': add_feed
}
