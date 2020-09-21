from datetime import datetime

# from src.core.queues.app import app
from src.core.requests.database import Database
from src.core.schemas.rss import RssFeed
from src.core.utils import make_hash


# @app.task()
def run_chain():
    chain = load_new_articles.s() | send_new_articles.s()
    chain()


# @app.task()
def load_new_articles():
    db = Database()
    active_feeds = db.get_active_feeds()
    if active_feeds is None:
        return

    for item in active_feeds:
        url_rss = item['url']
        chat_id = item['chat_id_id']
        feed = RssFeed(url=url_rss)
        articles = feed.parse()

        values_for_execute = []
        for article in articles:
            values_for_execute.append(
                (article.url, article.title, article.text, datetime.utcnow(),
                 False, make_hash(article.url, chat_id), chat_id)
            )
        db.insert_articles(values_for_execute)


# @app.task()
def send_new_articles():
    from pprint import pprint
    db = Database()
    ready_articles = db.get_ready_articles()
    pprint(ready_articles)


if __name__ == '__main__':
    send_new_articles()
