from django.contrib import admin

from .models import Article, RSS, User


admin.site.register(Article)
admin.site.register(RSS)
admin.site.register(User)


admin.site.site_title = 'RSS bot'
admin.site.site_header = 'RSS bot'
