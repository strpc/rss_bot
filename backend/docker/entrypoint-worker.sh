#!/bin/sh
set -e

beat() {
  sleep 60
  echo "Starting beat..."

  exec celery -A app.core.worker.worker_app:app_celery beat \
      --loglevel=${LOGLEVEL:-info} \
      --pidfile=
  }

worker() {
  echo "Starting worker..."

  exec celery -A app.core.worker.worker_app:app_celery worker
      --concurrency=${CONCURRENCY:-1} \
      -n rss_bot@%h \
      -Q rss_bot \
      --loglevel=${LOGLEVEL:-info}
  }


case "$1" in
  worker)
    shift
    worker
    ;;
  beat)
    shift
    beat
    ;;
  *)
    exec "$@"
    ;;
esac
