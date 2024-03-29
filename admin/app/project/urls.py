from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app.project.healthcheck import ping


ADMIN_URL = f"{settings.BASE_URL}/" if not settings.BASE_URL.endswith("/") else settings.BASE_URL

urlpatterns = [
    path(f"{ADMIN_URL[:-1]}/healthcheck/", ping),
    path(ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
