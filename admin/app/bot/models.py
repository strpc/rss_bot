# mypy: ignore-errors
from datetime import datetime

from django.db import models


class User(models.Model):
    chat_id = models.BigIntegerField("Chat ID", unique=True, null=False, blank=False)
    first_name = models.CharField("Имя", max_length=150, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, null=True, blank=True)
    username = models.CharField("Username", max_length=150, null=True, blank=True)
    register: datetime = models.DateTimeField("Зарегестрирован", auto_now_add=True)
    active = models.BooleanField("Активный", default=True)
    is_blocked = models.BooleanField("Заблокирован", default=False)

    def __str__(self) -> str:
        return (
            f'{self.first_name or ""} '
            f'{self.last_name or ""} '
            f'@{self.username or ""} '
            f'{self.register.astimezone().strftime("%d.%m.%Y %H:%M")}'
        )

    class Meta:
        db_table = "bot_users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class RSS(models.Model):
    url = models.CharField("URL RSS", max_length=2000, null=False, blank=False, unique=True)

    def __str__(self) -> str:
        return str(self.url)

    class Meta:
        db_table = "bot_rss"
        verbose_name = "RSS"
        verbose_name_plural = "RSS"


class RSSUsers(models.Model):
    user = models.ForeignKey(User, related_name="rss", on_delete=models.CASCADE)
    rss = models.ForeignKey(RSS, related_name="user", on_delete=models.CASCADE)
    added: datetime = models.DateTimeField("Добавлено", auto_now_add=True)
    updated: datetime = models.DateTimeField("Обновлено", auto_now_add=True)
    active = models.BooleanField("Активная", default=True, blank=False, null=False)

    class Meta:
        db_table = "bot_rss_user"
        verbose_name = "RSS"
        verbose_name_plural = "RSS"
        unique_together = (("user", "rss"),)


class Article(models.Model):
    rss: RSS = models.ForeignKey(RSS, related_name="article", on_delete=models.CASCADE)
    url = models.TextField("Ссылка на статью", blank=False, null=False)
    title = models.TextField("Заголовок статьи", blank=True, null=True)
    text = models.TextField("Текст статьи", blank=True, null=True)
    added = models.DateTimeField("Добавлено", auto_now_add=True)

    def __str__(self):
        return (
            f"{self.url} "
            # f'{self.added.astimezone().strftime("%d.%m.%Y %H:%M")}'
        )

    class Meta:
        db_table = "bot_articles"
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        unique_together = (("rss", "url"),)


class ArticleUser(models.Model):
    user: User = models.ForeignKey(User, related_name="article", on_delete=models.CASCADE)
    article: Article = models.ForeignKey(Article, related_name="user", on_delete=models.CASCADE)
    added = models.DateTimeField("Добавлено", auto_now_add=True)
    sended_at = models.DateTimeField("Время отправки", auto_now_add=False, null=True, blank=False)
    sended = models.BooleanField("Отправлено", default=False, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.article.title}"

    class Meta:
        db_table = "bot_user_articles"
        verbose_name = "Статья пользователя"
        verbose_name_plural = "Статьи пользователя"
        unique_together = (("user", "article"),)


class ServiceMessage(models.Model):
    title = models.CharField("Заголовок сообщения", max_length=250, blank=False, null=False)
    text = models.CharField("Текст сообщения", max_length=5000, blank=False, null=False)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "bot_service_message"
        verbose_name = "Сервисное сообщение"
        verbose_name_plural = "Сервисные сообщения"


class PocketIntegration(models.Model):
    user: User = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
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
