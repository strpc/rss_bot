from celery import Celery
from celery.schedules import crontab

from app.config import get_config


config = get_config()

app = Celery("rss_bot", broker=config.celery.broker, timezone="UTC")
app.control.purge()  # !DEV
app.autodiscover_tasks(
    [
        "app.tasks",
    ],
)
app.conf.task_default_queue = "rss_bot.download_articles_send_msg"
app.conf.beat_schedule = {
    "download_articles_send_msg": {
        "task": "tasks.run_chain",
        "schedule": crontab(
            hour=config.celery.hour_beat_interval,
            minute=config.celery.minute_beat_interval,
        ),
        "options": {"queue": "rss_bot.download_articles_send_msg"},
    },
}
