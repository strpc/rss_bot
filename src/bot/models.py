from datetime import datetime

from django.db import models


class User(models.Model):
    """Модель юзера"""
    chat_id = models.BigIntegerField('Chat ID', unique=True, null=False, blank=False)
    first_name = models.CharField('Имя', max_length=150, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, null=True, blank=True)
    username = models.CharField('Username', max_length=150, null=True, blank=True)
    register: datetime = models.DateTimeField('Зарегестрировался', auto_now_add=True)
    active = models.BooleanField('Активный', default=True)

    def __str__(self):
        return f'{self.first_name if self.first_name else ""} ' \
               f'{self.last_name if self.last_name else ""} ' \
               f'@{self.username if self.username else ""} ' \
               f'{self.register.astimezone().strftime("%d.%m.%Y %H:%M")}'

    class Meta:
        db_table = 'bot_users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class RSS(models.Model):
    """Фиды пользователей"""
    chat_id: User = models.ForeignKey(
        User, to_field='chat_id', verbose_name='Пользователь', on_delete=models.CASCADE
    )
    url = models.CharField('URL RSS', max_length=2000, null=False, blank=False)
    added: datetime = models.DateTimeField('Добавлено', auto_now_add=True)
    active = models.BooleanField('Активная', default=True, blank=False, null=False)
    chatid_url_hash = models.CharField(
        'Base64 hash', max_length=2500, null=False, blank=False, unique=True
    )

    def __str__(self):
        return f'{self.chat_id.first_name if self.chat_id.first_name else ""} ' \
               f'{self.chat_id.last_name if self.chat_id.last_name else ""} ' \
               f'@{self.chat_id.username if self.chat_id.username else ""} {self.url} ' \
               f'{self.added.astimezone().strftime("%d.%m.%Y %H:%M")}'

    class Meta:
        db_table = 'bot_users_rss'
        verbose_name = 'RSS пользователя'
        verbose_name_plural = 'RSS пользователей'


class Article(models.Model):
    """Статьи"""
    chat_id: User = models.ForeignKey(
        User, to_field='chat_id', verbose_name='Пользователь', on_delete=models.CASCADE
    )
    url_article = models.TextField('Ссылка на статью', blank=False, null=False)
    title = models.CharField('Заголовок статьи', max_length=1000, blank=True, null=True)
    text = models.CharField('Текст статьи', max_length=2000, blank=True, null=True)
    sended = models.BooleanField('Отправлено', default=False, blank=False, null=False)
    added: datetime = models.DateTimeField('Добавлено', auto_now_add=True)
    rss_url = models.ForeignKey(
        RSS, to_field='chatid_url_hash', verbose_name='RSS', on_delete=models.CASCADE
    )
    chatid_url_article_hash = models.CharField(
        'Base64 hash', max_length=2500, null=False, blank=False, unique=True
    )

    def __str__(self):
        return f'{self.chat_id.first_name if self.chat_id.first_name else ""}' \
               f' {self.chat_id.last_name if self.chat_id.last_name else ""} ' \
               f'@{self.chat_id.username if self.chat_id.username else ""} ' \
               f'{self.url_article} ' \
               f'{self.added.astimezone().strftime("%d.%m.%Y %H:%M")} Sended: {self.sended}'

    class Meta:
        db_table = 'bot_article'
        verbose_name = 'Статью'
        verbose_name_plural = 'Статьи'
