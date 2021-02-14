import json
import logging
from pprint import pprint
from typing import Union, Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from app.core.factory import Factory
from app.core.handlers import CommandHandler
from app.core.schemas.update import BaseMessage, BotCommand, TypeUpdate


logger = logging.getLogger(__name__)


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body = json.loads(request.body, encoding='utf-8')
        # logger.info(body)
        print('body:')
        pprint(body)
        message: Optional[Union[BaseMessage, BotCommand]] = Factory.register_message(body)
        if not message:
            # пришло какое-то событие, которое мы не отслеживаем.
            return JsonResponse({'success': 'true'}, status=200)
        print("\n\nfrom token_handler:")
        pprint(message.__dict__)
        if (message.type_update == TypeUpdate.command.value and
                message.command_raw in CommandHandler.__dict__.keys()):
            getattr(CommandHandler, message.command_raw)(message)

        elif (
                message.type_update == TypeUpdate.message.value
                or message.type_update == TypeUpdate.command.value
        ):
            pass  # пришло обычное сообщение. нужно сделать заглушку.
            print('обычное сообщение')
            print(message.text)

        return JsonResponse({'success': 'true'}, status=200)
