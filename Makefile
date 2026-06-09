.PHONY: help dev test lint db-reset docker-up docker-down logs

help:
	@echo "Available targets:"
	@echo "  dev          - Start development environment with docker-compose"
	@echo "  test         - Run pytest suite"
	@echo "  lint         - Run ruff linting"
	@echo "  db-reset     - Reset database (drop and recreate) and run migrations"
	@echo "  docker-up    - Start docker compose (detached)"
	@echo "  docker-down  - Stop docker compose"
	@echo "  logs         - Follow docker compose logs"

dev: docker-up
	@echo "Development environment started. Backend API available at http://localhost:8000"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

logs:
	docker compose logs -f

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .

db-reset:
	docker compose down -v
	docker compose up -d db
	@echo "Waiting for MySQL to be ready..."
	@./scripts/wait-for-db.sh
	cd backend && python migrate.py

.PHONY: help