#!/usr/bin/env bash

set -o errexit
set -o nounset

CONCURRENCY=${CONCURRENCY:-1}
LOGLEVEL=${LOGLEVEL:-info}
LOGFILE_CELERY=${LOGFILE_CELERY:-./bin/logs/celery_rss_bot.log}

celery -A src.core.queues.app:app worker \
    --concurrency=$CONCURRENCY \
    -n rss_bot@%h \
    -Q rss_bot.download_articles_send_msg \
    --loglevel=$LOGLEVEL \
    --logfile=$LOGFILE
