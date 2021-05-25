from app.project.settings import INTERVAL_BEAT_HOUR, INTERVAL_BEAT_MINUTE, RSS_BOT_BROKER
from celery import Celery, signals
from celery.schedules import crontab


app = Celery("rss_bot", broker=RSS_BOT_BROKER, timezone="UTC")
app.control.purge()  # !DEV
app.autodiscover_tasks(
    [
        "app.core.queues.tasks",
    ]
)
app.conf.task_default_queue = "rss_bot.download_articles_send_msg"
app.conf.beat_schedule = {
    "download_articles_send_msg": {
        "task": "src.core.queues.tasks.run_chain",
        "schedule": crontab(
            hour=INTERVAL_BEAT_HOUR,
            minute=INTERVAL_BEAT_MINUTE,
        ),
        "options": {"queue": "rss_bot.download_articles_send_msg"},
    }
}


@signals.celeryd_init.connect
def setup_log_format(sender, conf, **kwargs):
    """Делаем форматирование лога celery"""
    conf.worker_log_format = """
        [%(asctime)s: %(levelname)s/%(processName)s {0}] %(module)s: %(funcName)s:  %(message)s
    """.strip().format(
        sender
    )
    conf.worker_task_log_format = (
        "[%(asctime)s: %(levelname)s/%(processName)s {0}] "
        "[%(task_name)s(%(task_id)s)] %(message)s"
    ).format(sender)
