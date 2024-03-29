# Generated by Django 3.2.3 on 2021-11-20 23:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="RSS",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.CharField(max_length=2000, unique=True, verbose_name="URL RSS")),
            ],
            options={
                "verbose_name": "RSS",
                "verbose_name_plural": "RSS",
                "db_table": "bot_rss",
            },
        ),
        migrations.CreateModel(
            name="ServiceMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=250, verbose_name="Заголовок сообщения")),
                ("text", models.CharField(max_length=5000, verbose_name="Текст сообщения")),
            ],
            options={
                "verbose_name": "Сервисное сообщение",
                "verbose_name_plural": "Сервисные сообщения",
                "db_table": "bot_service_message",
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chat_id", models.BigIntegerField(unique=True, verbose_name="Chat ID")),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, null=True, verbose_name="Имя"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, null=True, verbose_name="Фамилия"),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        null=True,
                        verbose_name="Username",
                    ),
                ),
                (
                    "register",
                    models.DateTimeField(auto_now_add=True, verbose_name="Зарегестрирован"),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Активный")),
                ("is_blocked", models.BooleanField(default=False, verbose_name="Заблокирован")),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
                "db_table": "bot_users",
            },
        ),
        migrations.CreateModel(
            name="PocketIntegration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "request_token",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="Request token",
                    ),
                ),
                (
                    "access_token",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="Access token",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="username",
                    ),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Активный")),
                ("added", models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")),
                (
                    "updated",
                    models.DateTimeField(auto_now_add=True, null=True, verbose_name="Обновлено"),
                ),
                (
                    "error_code",
                    models.IntegerField(blank=True, null=True, verbose_name="Ошибка Pocket"),
                ),
                (
                    "error_message",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        null=True,
                        verbose_name="Сообщение ошибки Pocket",
                    ),
                ),
                (
                    "status_code",
                    models.IntegerField(blank=True, null=True, verbose_name="Статус код"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bot.user",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Интеграция с Pocket",
                "verbose_name_plural": "Интеграции с Pocket",
                "db_table": "bot_pocket_integration",
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.TextField(verbose_name="Ссылка на статью")),
                ("title", models.TextField(blank=True, null=True, verbose_name="Заголовок статьи")),
                ("text", models.TextField(blank=True, null=True, verbose_name="Текст статьи")),
                ("added", models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")),
                (
                    "rss",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="article",
                        to="bot.rss",
                    ),
                ),
            ],
            options={
                "verbose_name": "Статья",
                "verbose_name_plural": "Статьи",
                "db_table": "bot_articles",
                "unique_together": {("rss", "url")},
            },
        ),
        migrations.CreateModel(
            name="RSSUsers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("added", models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")),
                ("updated", models.DateTimeField(auto_now_add=True, verbose_name="Обновлено")),
                ("active", models.BooleanField(default=True, verbose_name="Активная")),
                (
                    "rss",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user",
                        to="bot.rss",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rss",
                        to="bot.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "RSS",
                "verbose_name_plural": "RSS",
                "db_table": "bot_rss_user",
                "unique_together": {("user", "rss")},
            },
        ),
        migrations.CreateModel(
            name="ArticleUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("added", models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")),
                ("sended_at", models.DateTimeField(null=True, verbose_name="Время отправки")),
                ("sended", models.BooleanField(default=False, verbose_name="Отправлено")),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user",
                        to="bot.article",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="article",
                        to="bot.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Статья пользователя",
                "verbose_name_plural": "Статьи пользователя",
                "db_table": "bot_user_articles",
                "unique_together": {("user", "article")},
            },
        ),
    ]
