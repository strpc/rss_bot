from celery import Celery
from celery.schedules import crontab

from app.config import get_config
from app.worker.logger import configure_logging


APP_NAME = "rss_bot"
TIMEZONE = "UTC"
DEFAULT_QUEUE = "rss_bot"
TASKS_NAMES = (
    "load_entries",
    "pocket_updater",
    "send_messages",
)

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

schedule_options = {
    "schedule": crontab(
        hour=config.celery.hour_beat_interval,
        minute=config.celery.minute_beat_interval,
    ),
    "options": {
        "queue": DEFAULT_QUEUE,
        "expires": 300,
    },
}

app_celery.conf.beat_schedule = {
    task_name: {
        "task": f"app.worker.tasks.{task_name}",
        **schedule_options,
    }
    for task_name in TASKS_NAMES
}
