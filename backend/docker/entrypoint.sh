#!/bin/bash
set -e

PORT=${RSS_BOT_PORT:-8000}
UVICORN_LOG_LEVEL=${UVICORN_LOG_LEVEL:-info}


prod() {
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --log-level ${UVICORN_LOG_LEVEL}
}

dev () {
    exec uvicorn app.main:app \
      --host 0.0.0.0 \
      --port ${PORT} \
      --log-level ${UVICORN_LOG_LEVEL} --reload
}


case "$1" in
  prod)
    shift
    prod
    ;;
  dev)
    shift
    dev
    ;;
  *)
    exec "$@"
    ;;
esac
