import json
import logging
import traceback

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.core import dispatcher

logger = logging.getLogger(__name__)


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body = json.loads(request.body, encoding='utf-8')
        logger.debug('%s\n-----------------------\n', body)
        try:
            dispatcher.process(body)
        except Exception as error:
            logger.error(error)
            logger.error(body)
            logger.error(traceback.format_exc())
        return JsonResponse({'success': 'true'}, status=200)
