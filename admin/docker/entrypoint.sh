#!/bin/sh


# !!!python ./app/manage.py loaddata --ignorenonexistent service_messages


PORT=${RSS_BOT_PORT:-8001}
LOG_LEVEL_UVICORN=${LOG_LEVEL_UVICORN:-info}

# Apply database migrations
echo "Apply database migrations"
python3 ./app/manage.py migrate --no-input


# Start server
echo "Starting server..."
dev() {
  echo "DEV mode"
  python3 ./app/manage.py runserver 0.0.0.0:${PORT}
}

prod() {
  echo "PROD mode"
  exec uvicorn app.project.asgi:application \
      --host 0.0.0.0 \
      --port ${PORT} \
      --log-level ${LOG_LEVEL_UVICORN}
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
