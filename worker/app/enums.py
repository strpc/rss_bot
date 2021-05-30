from enum import Enum


class ParseMode(str, Enum):
    MarkdownV2 = "MarkdownV2"
    HTML = "HTML"
    Markdown = "Markdown"
