from django.urls import path
from django.conf import settings

from .views import token_handler


urlpatterns = [
    path(settings.BOT_TOKEN, token_handler)
]
