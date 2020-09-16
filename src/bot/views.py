from pprint import pprint
from typing import Union
import logging
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpRequest

from src.core.factory import Factory
from src.core.schemas.update import BaseMessage, BotCommand, TypeUpdate
from src.core.handlers import CommandHandler


logger = logging.getLogger(__name__)


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        logger.info(body)
        pprint(body)
        message: Union[BaseMessage, BotCommand] = Factory.register_message(body)

        if message.type_update == TypeUpdate.command.name and \
                message.command_raw in CommandHandler.__dict__.keys():
            CommandHandler.__dict__[message.command_raw].__get__(CommandHandler)(message)

        elif message.type_update == TypeUpdate.message.name:
            pass  # пришло обычное сообщение. нужно сделать заглушку.

        return JsonResponse({'success': 'true'}, status=200)

