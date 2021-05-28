#!/usr/bin/env bash

set -o errexit
set -o nounset

LOGLEVEL=${LOGLEVEL:-info}
LOGFILE_BEAT=${LOGFILE_BEAT:-./bin/logs/beat_rss_bot.log}
PIDFILE=${PIDFILE:-/tmp/celerybeat_rss_bot.pid}

celery beat -A src.core.queues.app:app \
    --loglevel=$LOGLEVEL \
    --logfile=$LOGFILE_BEAT \
    --pidfile $PIDFILE
