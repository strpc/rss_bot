#!/bin/sh


PORT=${RSS_BOT_PORT:-8001}
LOG_LEVEL_UVICORN=${LOG_LEVEL_UVICORN:-info}

DEV_USERNAME=user
DEV_PASSWORD=hackme
DEV_EMAIL=admin@admin.ru


echo "Load fixtures service_messages..."
python3 ./app/manage.py loaddata --ignorenonexistent service_messages


# Apply database migrations
echo "Apply database migrations..."
python3 ./app/manage.py migrate --no-input


# Start server
echo "Starting server..."
dev() {
  echo "DEV mode"
  DJANGO_SUPERUSER_USERNAME=${DEV_USERNAME} \
  DJANGO_SUPERUSER_PASSWORD=${DEV_PASSWORD} \
  DJANGO_SUPERUSER_EMAIL=${DEV_EMAIL} python3 ./app/manage.py createsuperuser --no-input
  echo "user: ${DEV_USERNAME} password: ${DEV_PASSWORD}"

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
