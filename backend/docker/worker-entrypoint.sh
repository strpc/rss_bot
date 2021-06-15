#!/bin/sh
set -e

beat() {
  echo "Starting beat..."

  exec celery -A app.core.worker.worker_app:app_celery beat \
      --loglevel=${LOG_LEVEL:-info} \
      --pidfile=
  }

worker() {
  echo "Starting worker..."

  exec celery -A app.core.worker.worker_app:app_celery worker \
      -E \
      --concurrency=${CONCURRENCY:-1} \
      -n rss_bot@%h \
      -Q rss_bot \
      --loglevel=${LOG_LEVEL:-info}
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
