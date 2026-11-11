.PHONY: help dev test lint db-reset

help:
	@echo "Available targets:"
	@echo "  dev     - Start development server (uvicorn)"
	@echo "  test    - Run pytest suite"
	@echo "  lint    - Run ruff linting"
	@echo "  db-reset - Reset database and run migrations"

dev:
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .

db-reset:
	@echo "Aplique manualmente: mysql -u root -p < backend/schema.sql"

.PHONY: help
