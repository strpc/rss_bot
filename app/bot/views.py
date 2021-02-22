import json
import logging
import os
import traceback

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from easy_notifyer import Telegram, telegram_reporter

from app.core import dispatcher
from app.project.settings import DEBUG


logger = logging.getLogger(__name__)


if DEBUG is False and os.getenv("EASY_NOTIFYER_TELEGRAM_TOKEN") is not None:
    tg = Telegram()
    service_name = os.getenv("EASY_NOTIFYER_SERVICE_NAME")
    tg.send_message(f"service {service_name}: started...", disable_notification=True)
    dispatcher_wrapped = telegram_reporter()(dispatcher.process)
else:
    dispatcher_wrapped = dispatcher.process


@csrf_exempt
def token_handler(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        body = json.loads(request.body, encoding="utf-8")
        logger.debug("%s\n-----------------------\n", body)
        try:
            dispatcher_wrapped(body)
        except Exception as error:
            logger.error(error)
            logger.error(body)
            logger.error(traceback.format_exc())
        return JsonResponse({"success": "true"}, status=200)
