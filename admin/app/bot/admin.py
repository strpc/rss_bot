# mypy: ignore-errors
from django import forms
from django.contrib import admin

from .models import RSS, Article, PocketIntegration, ServiceMessage, User


class BaseAdminModel(admin.ModelAdmin):
    save_on_top = True
    save_as = True
    empty_value_display = "Недоступно"


@admin.register(User)
class UserAdmin(BaseAdminModel):
    fields = (
        "chat_id",
        "first_name",
        "last_name",
        "username",
        "register",
        "active",
        "view_rss_feeds",
    )
    readonly_fields = (
        "chat_id",
        "first_name",
        "last_name",
        "username",
        "register",
        "view_rss_feeds",
    )
    list_display = (
        "username",
        "register",
        "active",
    )
    list_display_links = (
        "username",
        "register",
        "active",
    )
    list_filter = ("active",)

    def view_rss_feeds(self, obj):
        rss_query = RSS.objects.filter(chat_id=obj.chat_id, active=True)
        result = ""
        for item in rss_query:
            result += f"{item.url}\n"
        return result

    view_rss_feeds.short_description = "Active RSS"


@admin.register(RSS)
class AdminRss(BaseAdminModel):
    fields = (
        "view_username",
        "url",
        "added",
        "active",
    )
    readonly_fields = ("url", "added", "view_username")
    exclude = ("chatid_url_hash",)
    list_display = (
        "view_username",
        "url",
        "added",
        "active",
    )
    list_display_links = ("url", "added", "active", "view_username")
    list_filter = (
        "chat_id__username",
        "active",
        "url",
    )

    def view_username(self, obj):
        return view_username(obj)

    view_username.short_description = "Username"


@admin.register(Article)
class AdminArticle(BaseAdminModel):
    ordering = ("added", "chat_id__pk")
    fields = (
        "view_username",
        "title",
        "get_rss_url",
        "added",
        "sended",
        "text",
    )
    readonly_fields = (
        "view_username",
        "title",
        "get_rss_url",
        "added",
        "sended",
        "text",
    )
    list_display = ("view_username", "title", "get_rss_url", "added", "sended")
    list_display_links = (
        "view_username",
        "title",
        "get_rss_url",
        "added",
    )
    list_filter = (
        "sended",
        "chat_id__username",
        "rss_url__url",
    )

    def view_username(self, obj):
        return view_username(obj)

    view_username.short_description = "Username"


def view_username(obj):
    return f"@{obj.chat_id.username}"


class ServiceMessageForm(forms.ModelForm):
    class Meta:
        model = ServiceMessage
        fields = "__all__"
        widgets = {
            "text": forms.Textarea(attrs={"cols": 80, "rows": 20}),
        }


@admin.register(ServiceMessage)
class AdminServiceMessage(BaseAdminModel):
    fields = ("title", "text")
    ordering = ("title", "text")
    list_display = ("title", "text")
    list_display_links = ("title", "text")
    form = ServiceMessageForm


@admin.register(PocketIntegration)
class AdminPocketIntegration(BaseAdminModel):
    fields = ("user", "request_token", "access_token", "active", "added")
    list_display = ("user", "active", "added")
    list_display_links = ("user", "active", "added")
    ordering = ("active", "added", "user")
    readonly_fields = ("user", "request_token", "access_token", "added")


admin.site.site_title = "RSS bot"
admin.site.site_header = "RSS bot"
