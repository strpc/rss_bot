from dataclasses import dataclass


@dataclass
class User:
    id = "id"
    chat_id = "chat_id"
    first_name = "first_name"
    last_name = "last_name"
    username = "username"
    register = "register"
    active = "active"
    is_blocked = "is_blocked"

    @dataclass
    class Meta:
        tablename = "bot_users"


@dataclass
class RSSFields:
    id = "id"
    url = "url"

    @dataclass
    class Meta:
        tablename = "bot_rss"


@dataclass
class RSSUsers:
    id = "id"
    url = "url"
    user_id = "user_id"
    rss_id = "rss_id"
    added = "added"
    updated = "updated"
    active = "active"

    @dataclass
    class Meta:
        tablename = "bot_rss_user"


@dataclass
class Article:
    id = "id"
    rss_id = "rss_id"
    url = "url"
    title = "title"
    text = "text"
    added = "added"

    @dataclass
    class Meta:
        tablename = "bot_articles"


@dataclass
class ArticleUser:
    id = "id"
    user_id = "user_id"
    article_id = "article_id"
    added = "added"
    sended_at = "sended_at"
    sended = "sended"

    @dataclass
    class Meta:
        tablename = "bot_user_articles"


@dataclass
class ServiceMessage:
    id = "id"
    title = "title"
    text = "text"

    @dataclass
    class Meta:
        tablename = "bot_service_message"


@dataclass
class PocketIntegration:
    id = "id"
    user_id = "user_id"
    request_token = "request_token"
    access_token = "access_token"
    username = "username"
    active = "active"
    added = "added"
    updated = "updated"
    error_code = "error_code"
    error_message = "error_message"
    status_code = "status_code"

    @dataclass
    class Meta:
        tablename = "bot_pocket_integration"
