from django.contrib import admin

from .models import Article, RSS, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    save_on_top = True
    save_as = True
    empty_value_display = "Недоступно"
    fields = (
        'chat_id', 'first_name', 'last_name', 'username',
        'register', 'active', 'view_rss_feeds',
    )
    readonly_fields = (
        'chat_id', 'first_name', 'last_name', 'username',
        'register', 'view_rss_feeds',
    )
    list_display = (
        'username', 'register', 'active',
    )
    list_display_links = (
        'username', 'register', 'active',
    )
    list_filter = (
        'active',
    )

    def view_rss_feeds(self, obj):
        rss_query = RSS.objects.filter(chat_id=obj.chat_id, active=True)
        result = ''
        for item in rss_query:
            result += f"{item.url}\n"
        return result

    view_rss_feeds.short_description = 'Active RSS'


@admin.register(RSS)
class AdminRss(admin.ModelAdmin):
    save_on_top = True
    save_as = True
    empty_value_display = "Недоступно"
    fields = (
        'view_username', 'url', 'added', 'active',
    )
    readonly_fields = (
        'url', 'added', 'view_username'
    )
    exclude = (
        'chatid_url_hash',
    )
    list_display = (
        'view_username', 'url', 'added', 'active',
    )
    list_display_links = (
        'url', 'added', 'active', 'view_username'
    )
    list_filter = (
        'chat_id__username', 'active', 'url',
    )

    def view_username(self, obj):
        return view_username(obj)
    view_username.short_description = 'Username'


@admin.register(Article)
class AdminArticle(admin.ModelAdmin):
    save_on_top = True
    save_as = True
    empty_value_display = "Недоступно"
    ordering = ('added', 'chat_id__pk')
    fields = (
        'view_username', 'title', 'get_rss_url', 'added', 'sended'
    )
    readonly_fields = (
        'view_username', 'title', 'get_rss_url', 'added', 'sended'
    )
    list_display = (
        'view_username', 'title', 'get_rss_url', 'added', 'sended'
    )
    list_display_links = (
        'view_username', 'title', 'get_rss_url', 'added',
    )
    list_filter = (
        'sended', 'chat_id__username', 'rss_url__url',
    )

    def view_username(self, obj):
        return view_username(obj)
    view_username.short_description = 'Username'


def view_username(obj):
    return f"@{obj.chat_id.username}"


admin.site.site_title = 'RSS bot'
admin.site.site_header = 'RSS bot'
