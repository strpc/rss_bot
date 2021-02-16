from datetime import datetime

from app.core.queues.app import app
from app.core.requests.database import Database
from app.core.schemas.rss import RssFeed
from app.core.schemas.update import FromDB
from app.core.utils import get_hash
from app.project.settings import COUNT_TEXT_SYMBOL, COUNT_TITLE_SYMBOL, PARSE_MODE_MARKDOWN


@app.task()
def run_chain():
    chain = load_new_articles.s() | send_new_articles.s()
    chain()


@app.task()
def load_new_articles(*args, **kwargs):
    db = Database()
    active_feeds = db.get_active_feeds()
    if active_feeds is None:
        return

    for item in active_feeds:
        url_rss = item["url"]
        chat_id = item["chat_id_id"]
        rss_hash = item["chatid_url_hash"]
        feed = RssFeed(url=url_rss)
        articles = feed.parse()

        values_for_execute = []
        for article in articles:
            values_for_execute.append(
                (
                    article.url,
                    article.title,
                    article.text,
                    datetime.utcnow(),
                    False,
                    get_hash(article.url, chat_id),
                    rss_hash,
                    chat_id,
                )
            )
        db.insert_articles(values_for_execute)


@app.task()
def send_new_articles(*args, **kwargs):
    db = Database()
    ready_articles = db.get_ready_articles()
    values_for_execute = []
    if ready_articles is None:
        return
    for item in ready_articles:
        text = f"*{item['title'][:COUNT_TITLE_SYMBOL]}*\n\n" if item["title"] else ""
        text += f"{item['text'][:COUNT_TEXT_SYMBOL]}...\n\n" if item["text"] else ""
        text += item["url_article"]

        message = FromDB(item["chat_id_id"])
        response = message.send_message(text, PARSE_MODE_MARKDOWN, False)

        values_for_execute.append((item["url_article"], item["chat_id_id"]))

        if (
            response.status_code != 200
            and response.json().get("description") == "Forbidden: bot was blocked by the user"
        ):
            # пользователь остановил бота
            db.disable_user(item["chat_id_id"])
        elif response.status_code != 200:
            message.send_message(text.replace("*", ""), disable_web_page_preview=False)
    db.mark_sended(values_for_execute)
