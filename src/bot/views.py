import logging
import json
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpRequest


LOGGER = logging.getLogger(__name__)


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        LOGGER.info(body)
        pprint(body)
        # message: Message = Factory.register_message(body)
        # handlers.process_message(message)
        response = JsonResponse({'success': 'true'}, status=200)
        return response
