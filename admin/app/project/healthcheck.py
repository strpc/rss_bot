from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ping(_: HttpRequest) -> JsonResponse:
    return JsonResponse({}, status=200)
