from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ping(_: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HTTPStatus.OK)
