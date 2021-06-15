from celery import Celery
from celery.schedules import crontab

from app.config import get_config
from app.core.worker.logger import configure_logging


config = get_config()
configure_logging(config.app.log_level)

app_celery = Celery("rss_bot", broker=config.celery.broker, timezone="UTC")


if config.app.debug:
    app_celery.control.purge()


app_celery.autodiscover_tasks(
    [
        "app.core.worker.tasks",
    ],
)
app_celery.conf.task_default_queue = "rss_bot"
app_celery.conf.beat_schedule = {
    "chain": {
        "task": "app.core.worker.tasks.run_chain",
        "schedule": crontab(
            hour=config.celery.hour_beat_interval,
            minute=config.celery.minute_beat_interval,
        ),
        "options": {"queue": "rss_bot"},
    },
}
