from enum import Enum, unique


@unique
class InternalMessages(str, Enum):
    hello_user = "hello_user"
    help = "help"
    unsupported_update = "unsupported_update"
    incorrect_rss = "incorrect_rss"
    not_have_active = "not_have_active"
    url_not_founded = "url_not_founded"
    already_added_feed = "already_added_feed"
    limit_achieved = "limit_achieved"
    integrations = "integrations"
    unauthorize_pocket = "unauthorize_pocket"
    error = "error"
