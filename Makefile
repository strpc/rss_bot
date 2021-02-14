PYTHON=.venv/bin/python3
MANAGEPY=app/manage.py
.DEFAULT_GOAL := run

run:
	$(PYTHON) $(MANAGEPY) runsslserver 0.0.0.0:8000 --certificate cert.pem --key private.key

db_migrate:
	make makemigrations_django && make migrate_django

makemigrations_django:
	$(PYTHON) $(MANAGEPY) makemigrations

migrate_django:
	$(PYTHON) $(MANAGEPY) migrate

celery:
	 celery -A app.core.queues.app:app worker --loglevel=info -n rss_bot@%h -Q rss_bot.download_articles_send_msg --loglevel=info

beat:
	 celery beat -A app.core.queues.app:app --loglevel=info

shutdown_celery:
	celery control shutdown

status_celery:
	celery inspect active_queues

tasks_celery:
	celery inspect registered

up:
	docker-compose up -d

upb:
	docker-compose up -d --force-recreate --build

down:
	docker-compose down
