from enum import Enum


class ServiceMessage(str, Enum):
    hello_user = "hello_user"
    unsupported_update = "unsupported_update"
    show_help = "show_help"
    incorrect_rss = "incorrect_rss"
    not_have_active = "not_have_active"
    url_not_founded = "url_not_founded"
    already_added_feed = "already_added_feed"
    limit_achieved = "limit_achieved"
    authorize_message = "authorize_message"
    unauthorize_message = "unauthorize_message"
    error = "error"
