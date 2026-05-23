SHELL := /bin/sh

.PHONY: up down logs lint test

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f api-gateway users-service tasks-service analytics-service db

lint:
	docker run --rm -v $(PWD):/app -w /app python:3.12-slim sh -c "pip install -q ruff && ruff check ."

test:
	docker run --rm -v $(PWD):/app -w /app python:3.12-slim sh -c "pip install -q -r requirements-dev.txt && pytest"
