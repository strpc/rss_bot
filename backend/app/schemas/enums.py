from enum import Enum


class ParseMode(str, Enum):
    MarkdownV2 = "MarkdownV2"
    HTML = "HTML"
    Markdown = "Markdown"


class TypeEntity(str, Enum):
    url = "url"
    bot_command = "bot_command"
    code = "code"
    mention = "mention"
    hashtag = "hashtag"
    cashtag = "cashtag"
    email = "email"
    phone_number = "phone_number"
    bold = "bold"
    italic = "italic"
    underline = "underline"
    strikethrough = "strikethrough"
    pre = "pre"
    text_link = "text_link"
    text_mention = "text_mention"


class TypeUpdate(str, Enum):
    message = "message"
    callback = "callback"
    # edited_message = "edited_message"


class TypeChat(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"
