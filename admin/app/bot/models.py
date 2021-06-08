# mypy: ignore-errors
from datetime import datetime

from django.db import models


class User(models.Model):
    """Модель юзера."""

    chat_id = models.BigIntegerField("Chat ID", unique=True, null=False, blank=False)
    first_name = models.CharField("Имя", max_length=150, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, null=True, blank=True)
    username = models.CharField("Username", max_length=150, null=True, blank=True)
    register: datetime = models.DateTimeField("Зарегестрирован", auto_now_add=True)
    active = models.BooleanField("Активный", default=True)

    def __str__(self):
        return (
            f'{self.first_name if self.first_name else ""} '
            f'{self.last_name if self.last_name else ""} '
            f'@{self.username if self.username else ""} '
            f'{self.register.astimezone().strftime("%d.%m.%Y %H:%M")}'
        )

    class Meta:
        db_table = "bot_users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class RSS(models.Model):
    """Фиды пользователей."""

    chat_id: User = models.ForeignKey(
        User,
        to_field="chat_id",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    url = models.CharField("URL RSS", max_length=2000, null=False, blank=False)
    added: datetime = models.DateTimeField("Добавлено", auto_now_add=True)
    active = models.BooleanField("Активная", default=True, blank=False, null=False)
    chatid_url_hash = models.CharField(
        "Base64 hash",
        max_length=2500,
        null=False,
        blank=False,
        unique=True,
    )

    def __str__(self):
        return (
            f'{self.chat_id.first_name if self.chat_id.first_name else ""} '
            f'{self.chat_id.last_name if self.chat_id.last_name else ""} '
            f'@{self.chat_id.username if self.chat_id.username else ""} {self.url} '
            f'{self.added.astimezone().strftime("%d.%m.%Y %H:%M")}'
        )

    class Meta:
        db_table = "bot_users_rss"
        verbose_name = "RSS пользователя"
        verbose_name_plural = "RSS пользователей"


class Article(models.Model):
    """Статьи."""

    chat_id: User = models.ForeignKey(
        User,
        to_field="chat_id",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
    )
    url_article = models.TextField("Ссылка на статью", blank=False, null=False)
    title = models.CharField("Заголовок статьи", max_length=1000, blank=True, null=True)
    text = models.CharField("Текст статьи", max_length=2000, blank=True, null=True)
    sended = models.BooleanField("Отправлено", default=False, blank=False, null=False)
    added: datetime = models.DateTimeField("Добавлено", auto_now_add=True)
    rss_url: RSS = models.ForeignKey(
        RSS,
        to_field="chatid_url_hash",
        verbose_name="RSS",
        on_delete=models.CASCADE,
    )
    chatid_url_article_hash = models.CharField(
        "Base64 hash",
        max_length=2500,
        null=False,
        blank=False,
        unique=True,
    )

    def get_rss_url(self):
        result = str(self.rss_url.url)
        return result[:40] if len(result) < 41 else result[:40] + "..."

    get_rss_url.short_description = "RSS url"

    def __str__(self):
        return (
            f'{self.chat_id.first_name if self.chat_id.first_name else ""}'
            f' {self.chat_id.last_name if self.chat_id.last_name else ""} '
            f'@{self.chat_id.username if self.chat_id.username else ""} '
            f"{self.url_article} "
            f'{self.added.astimezone().strftime("%d.%m.%Y %H:%M")} Sended: {self.sended}'
        )

    class Meta:
        db_table = "bot_article"
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


class ServiceMessage(models.Model):
    """Сервисные сообщения."""

    title = models.CharField("Заголовок сообщения", max_length=250, blank=False, null=False)
    text = models.CharField("Текст сообщения", max_length=5000, blank=False, null=False)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "bot_service_message"
        verbose_name = "Сервисное сообщение"
        verbose_name_plural = "Сервисные сообщения"


class PocketIntegration(models.Model):
    user: User = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        unique=True,
    )
    request_token = models.CharField("Request token", max_length=250, blank=True, null=True)
    access_token = models.CharField("Access token", max_length=250, blank=True, null=True)
    username = models.CharField("username", max_length=250, blank=True, null=True)
    active = models.BooleanField("Активный", default=True)
    added: datetime = models.DateTimeField("Добавлено", auto_now_add=True)
    updated: datetime = models.DateTimeField("Обновлено", auto_now_add=True, null=True, blank=True)
    error_code = models.IntegerField("Ошибка Pocket", null=True, blank=True)
    error_message = models.CharField(
        "Сообщение ошибки Pocket",
        max_length=250,
        null=True,
        blank=True,
    )
    status_code = models.IntegerField("Статус код", null=True, blank=True)

    class Meta:
        db_table = "bot_pocket_integration"
        verbose_name = "Интеграция с Pocket"
        verbose_name_plural = "Интеграции с Pocket"
