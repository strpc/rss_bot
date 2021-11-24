# # mypy: ignore-errors
from typing import List, Tuple

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import RSS, Article, ArticleUser, PocketIntegration, RSSUsers, ServiceMessage, User
from .utils import limit_word


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
        "user_rss",
        "active",
        "is_blocked",
    )
    readonly_fields = (
        (
            "register",
            "user_rss",
        )
        if settings.DEBUG
        else ("chat_id", "first_name", "last_name", "username", "register", "user_rss")
    )
    list_display = (
        "username",
        "register",
        "active",
        "is_blocked",
    )
    list_display_links = (
        "username",
        "register",
        "active",
        "is_blocked",
    )
    list_filter = ("active", "is_blocked")

    def user_rss(self, obj: User) -> str:
        return obj.rss.url  # type: ignore

    user_rss.short_description = "RSS"  # type: ignore


@admin.register(RSS)
class AdminRSS(admin.ModelAdmin):
    list_display = ("url",)
    list_display_links = ("url",)


class URLFilter(SimpleListFilter):
    title = "URL RSS"
    parameter_name = "rss__url"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> List[Tuple[str, str]]:
        qs = model_admin.get_queryset(request)
        return [
            (url.rss.url, limit_word(url.rss.url, settings.LIMIT_SYMBOLS_ADMIN_FIELDS))
            for url in qs
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            params = {self.parameter_name: self.value()}
            return queryset.filter(**params)
        else:
            return queryset.filter()


@admin.register(RSSUsers)
class AdminRSSUsers(BaseAdminModel):
    fields = (
        "user",
        "rss",
        "active",
        "added",
        "updated",
    )
    readonly_fields = ("added", "updated")
    list_display = (
        "user",
        "rss",
        "active",
        "added",
        "updated",
    )
    list_display_links = (
        "user",
        "rss",
        "active",
        "added",
        "updated",
    )
    list_filter = (
        "user__username",
        URLFilter,
        "active",
    )


class URLArticleFilter(URLFilter):
    parameter_name = "article__rss__url"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> List[Tuple[str, str]]:
        qs = model_admin.get_queryset(request)
        return [
            (
                url.article.rss.url,
                limit_word(url.article.rss.url, settings.LIMIT_SYMBOLS_ADMIN_FIELDS),
            )
            for url in qs
        ]


@admin.register(ArticleUser)
class AdminArticleUser(BaseAdminModel):
    ordering = ("-added", "user__pk")
    fields = (
        "user",
        "article",
        "added",
        "sended_at",
        "sended",
    )
    readonly_fields = (
        "added",
        "sended_at",
    )
    list_display = (
        "user",
        "get_title_article",
        "added",
        "sended_at",
        "sended",
    )
    list_display_links = (
        "user",
        "get_title_article",
        "added",
        "sended_at",
        "sended",
    )
    list_filter = (
        "sended",
        "user__username",
        URLArticleFilter,
    )

    def get_title_article(self, obj: ArticleUser) -> str:
        return obj.article.title

    get_title_article.short_description = "Заголовок статьи"  # type: ignore


@admin.register(Article)
class AdminArticle(BaseAdminModel):
    ordering = ("-added",)
    fields = (
        "title",
        "text",
        "url",
        "rss",
        "added",
    )
    readonly_fields = ("added",)
    list_display = (
        "title",
        "url",
        "get_rss_url",
        "added",
    )
    list_display_links = (
        "title",
        "url",
        "get_rss_url",
        "added",
    )
    list_filter = (URLFilter,)

    def get_rss_url(self, obj: Article) -> str:
        return obj.rss.url

    get_rss_url.short_description = "RSS url"  # type: ignore


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
    fields = (
        "user",
        "request_token",
        "access_token",
        "active",
        "added",
        "error_code",
        "error_message",
        "status_code",
    )
    list_display = (
        "user",
        "active",
        "added",
        "updated",
        "error_code",
        "error_message",
        "status_code",
    )
    list_display_links = ("user", "active", "added", "updated")
    ordering = ("active", "added", "updated", "user")
    readonly_fields = (
        "user",
        "request_token",
        "access_token",
        "added",
        "updated",
        "error_code",
        "error_message",
        "status_code",
    )


admin.site.site_title = "RSS bot"
admin.site.site_header = "RSS bot"
