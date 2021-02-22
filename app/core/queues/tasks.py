from app.core.clients import Requests, Telegram
from app.core.db import SQLiteDB
from app.core.queues.app import app
from app.core.services.feed import Article, Feed
from app.core.utils import get_hash
from app.project.settings import (
    COUNT_ARTICLE_UPDATE,
    COUNT_TEXT_SYMBOL,
    COUNT_TITLE_SYMBOL,
    DB_PATH,
    PARSE_MODE_MARKDOWN,
    RSS_BOT_TOKEN,
)


@app.task()
def run_chain():
    chain = load_new_articles.s() | send_new_articles.s()
    chain()


@app.task()
def load_new_articles(*args, **kwargs):
    with SQLiteDB(DB_PATH) as db:
        active_feeds = db.get_active_feeds()
        if active_feeds is None:
            return

        for item in active_feeds:
            url_rss = item["url"]
            chat_id = item["chat_id"]
            rss_hash = item["chatid_url_hash"]

            feed = Feed(url=url_rss)
            values_for_execute = []

            for article_raw in feed.parse(limit=COUNT_ARTICLE_UPDATE):
                article = Article(
                    url=article_raw.get("link"),
                    text=article_raw.get("summary"),
                    title=article_raw.get("title"),
                )
                values_for_execute.append(
                    (
                        article.url,
                        article.title,
                        article.text,
                        False,
                        get_hash(article.url, chat_id),
                        rss_hash,
                        chat_id,
                    )
                )
                db.insert_articles(values_for_execute)


@app.task()
def send_new_articles(*args, **kwargs):
    with SQLiteDB(DB_PATH) as db:
        ready_articles = db.get_ready_articles()
        if ready_articles is None:
            return
        telegram = Telegram(token=RSS_BOT_TOKEN, client=Requests())

        values_for_execute = []
        for item in ready_articles:
            text = f"*{item['title'][:COUNT_TITLE_SYMBOL]}*\n\n" if item["title"] else ""
            text += f"{item['text'][:COUNT_TEXT_SYMBOL]}...\n\n" if item["text"] else ""
            text += item["url_article"]

            response = telegram.send_message(
                chat_id=item["chat_id"],
                text=text,
                parse_mode=PARSE_MODE_MARKDOWN,
                disable_web_page_preview=False,
            )

            values_for_execute.append((item["url_article"], item["chat_id_id"]))

            if (
                response.status_code != 200
                and response.json().get("description") == "Forbidden: bot was blocked by the user"
            ):
                # пользователь остановил бота
                db.disable_user(item["chat_id"])
            elif response.status_code != 200:
                telegram.send_message(
                    chat_id=item["chat_id"],
                    text=text.replace("*", ""),
                    disable_web_page_preview=False,
                )
        db.mark_sended(values_for_execute)
