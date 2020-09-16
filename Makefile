PYTHON=.venv/bin/python3
MANAGEPY=src/manage.py

#run:
	#$(PYTHON) $(MANAGEPY) runserver 0.0.0.0:8080

db_change:
	make makemigrations_django && make migrate_django

makemigrations_django:
	$(PYTHON) $(MANAGEPY) makemigrations

migrate_django:
	$(PYTHON) $(MANAGEPY) migrate

#celery:
	# celery -A src.core.app_celery:app worker --loglevel=info

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
