from celery import Celery, signals
from celery.schedules import crontab

from src.project.settings import BOT_BROKER, INTERVAL_RUN_SEND


app = Celery('rss_bot', broker=BOT_BROKER, timezone='UTC')
app.control.purge()  # !DEV
app.autodiscover_tasks([
    'src.core.queues.tasks',
])
app.conf.beat_schedule = {
    "download_articles_send_msg": {
        "task": "rss_bot.run_chain",
        "schedule": crontab(minute=f"*/{INTERVAL_RUN_SEND}"),
    }
}


@signals.celeryd_init.connect
def setup_log_format(sender, conf, **kwargs):
    """Делаем форматирование лога celery"""
    conf.worker_log_format = """
        [%(asctime)s: %(levelname)s/%(processName)s {0}] %(module)s: %(funcName)s:  %(message)s
    """.strip().format(sender)
    conf.worker_task_log_format = (
        '[%(asctime)s: %(levelname)s/%(processName)s {0}] '
        '[%(task_name)s(%(task_id)s)] %(message)s'
    ).format(sender)
