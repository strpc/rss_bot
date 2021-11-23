from celery import Celery
from celery.schedules import crontab

from app.config import get_config
from app.worker.logger import configure_logging


APP_NAME = "rss_bot"
TIMEZONE = "UTC"
DEFAULT_QUEUE = "rss_bot"

config = get_config()
configure_logging(config.app.log_level)

app_celery = Celery(APP_NAME, broker=config.celery.broker, timezone=TIMEZONE)


if config.app.debug:
    app_celery.control.purge()


app_celery.autodiscover_tasks(
    [
        "app.worker.tasks",
    ],
)
app_celery.conf.task_default_queue = DEFAULT_QUEUE
app_celery.conf.beat_schedule = {
    "chain": {
        "task": "app.worker.tasks.run_chain",
        "schedule": crontab(
            hour=config.celery.hour_beat_interval,
            minute=config.celery.minute_beat_interval,
        ),
        "options": {"queue": "rss_bot"},
    },
}
