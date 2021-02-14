import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.core.handlers import dispatcher

logger = logging.getLogger(__name__)


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body = json.loads(request.body, encoding='utf-8')
        logger.debug(body)
        dispatcher.process(body)
        return JsonResponse({'success': 'true'}, status=200)
