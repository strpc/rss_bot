

class BaseMessage:
    pass

class Command(BaseMessage):
    def __init__(self, **kwargs):
        _message = kwargs.get('message')
        self.chat_id = _message.get('chat').get('id')
        self.first_name = _message.get('chat').get('first_name')
        self.last_name = _message.get('chat').get('last_name')
        self.username = _message.get('chat').get('username')
        self.date = _message.get('date')
        self.command = _message.get('text')
        self.type = 'command'


class Message(BaseMessage):
    def __init__(self, **kwargs):


        # {'message': {'chat': {'first_name': 'твой братишка',
        #                       'id': 126471094,
        #                       'type': 'private',
        #                       'username': 'your_brother'},
        #              'date': 1600243284,
        #              'entities': [{'length': 6, 'offset': 0, 'type': 'bot_command'}],
        #              'from': {'first_name': 'твой братишка',
        #                       'id': 126471094,
        #                       'is_bot': False,
        #                       'language_code': 'ru',
        #                       'username': 'your_brother'},
        #              'message_id': 27,
        #              'text': '/start'},
        #  'update_id': 747686986}

        # {'message': {'chat': {'first_name': 'твой братишка',
        #                       'id': 126471094,
        #                       'type': 'private',
        #                       'username': 'your_brother'},
        #              'date': 1600242742,
        #              'from': {'first_name': 'твой братишка',
        #                       'id': 126471094,
        #                       'is_bot': False,
        #                       'language_code': 'ru',
        #                       'username': 'your_brother'},
        #              'message_id': 26,
        #              'text': 'kl'},
        #  'update_id': 747686985}
