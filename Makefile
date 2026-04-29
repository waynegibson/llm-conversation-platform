COMPOSE ?= podman compose
PYTHON ?= .venv/bin/python
RUFF ?= .venv/bin/ruff
PYTEST ?= .venv/bin/pytest
GIT ?= git
msg ?= new migration
VERSION ?=

.PHONY: up down logs rebuild migrate revision bootstrap lint format test check hooks-install tag tag-push release-check

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api

rebuild:
	$(COMPOSE) build --no-cache api

migrate:
	$(COMPOSE) exec api alembic upgrade head

revision:
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(msg)"

bootstrap:
	bash scripts/bootstrap.sh

lint:
	$(RUFF) check app tests

format:
	$(RUFF) format app tests

test:
	$(PYTEST)

check: lint test

hooks-install:
	.venv/bin/pre-commit install

release-check:
	@test -n "$(VERSION)" || (echo "Usage: make tag VERSION=v0.1.0" >&2; exit 1)

tag: release-check check
	$(GIT) tag -a $(VERSION) -m "Release $(VERSION)"

tag-push: release-check
	$(GIT) push origin $(VERSION)
