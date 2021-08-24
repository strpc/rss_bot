include .env

.SILENT:
.DEFAULT_GOAL := run

env_file = .env
PYTHON=.venv/bin/python3
MANAGEPY=admin/app/manage.py

export $(shell sed 's/=.*//' $(env_file))

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

isort:
	git status -s --untracked-files=no | awk '{ print $2}' | xargs isort --lines-after-imports=2

black:
	black --check --diff app

clean:
	@rm -rf `find . -name __pycache__`
	@rm -rf `find . -name .hash`
	@rm -rf `find . -name .md5`  # old styling
	@rm -f `find . -type f -name '*.py[co]' `
	@rm -f `find . -type f -name '*~' `
	@rm -f `find . -type f -name '.*~' `
	@rm -f `find . -type f -name '@*' `
	@rm -f `find . -type f -name '#*#' `
	@rm -f `find . -type f -name '*.orig' `
	@rm -f `find . -type f -name '*.rej' `
	@rm -f `find . -type f -name '*.md5' `  # old styling
	@rm -f .coverage
	@rm -rf htmlcov
	@rm -rf build
	@rm -rf *.egg-info
	@rm -rf cover
	@rm -rf .tox
	@rm -f .develop
	@rm -f .flake
	@rm -f .install-deps
	@rm -f .install-cython

django:
	cd admin && DEBUG=True python3 app/manage.py runserver

run_backend:
	PYTHONPATH=$(shell pwd)/backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
