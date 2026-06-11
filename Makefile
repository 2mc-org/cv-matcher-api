.PHONY: install run test format lint clean run-debug db-generate db-up db-down db-current install-prod run-prod erd-generate docs-generate generate-twenty-graphql

# Default port
PORT ?= 8000
MICROSERVICE_PORT ?= 8001

# Load environment variables from .env file
include .env
export

# Install dependencies
install:
	uv sync --extra dev

# Install production dependencies
install-prod:
	uv pip install .

# Run development server
run:
	uvicorn app.main:app --reload --port $(PORT)

# Run production server
run-prod:
	uv run uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --workers 1

# Run server in debug mode with debugpy
run-debug:
	PYDEVD_DISABLE_FILE_VALIDATION=1 python -Xfrozen_modules=off -m debugpy --listen 5678 -m uvicorn app.main:app --reload --port $(PORT) --host 0.0.0.0

run-debug-with-wait:
	PYDEVD_DISABLE_FILE_VALIDATION=1 python -Xfrozen_modules=off -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload --port $(PORT) --host 0.0.0.0

# Run tests
test:
	pytest

# Format code
format:
	uv run ruff format .
	uv run ruff check --fix .

# Check code
lint:
	uv run ruff check .
	uv run basedpyright .

lint-fix:
	uv run ruff format .
	uv run ruff check --fix .
	uv run basedpyright .

# Clean cache and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".pyright_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "coverage_html" -exec rm -r {} +
	find . -type f -name "coverage.xml" -delete

# Database migrations
db-generate:
	@read -p "Enter migration message: " message; \
	uv run alembic revision --autogenerate -m "$$message"

# Apply all migrations
db-up:
	uv run alembic upgrade head

# Downgrade one migration
db-down:
	uv run alembic downgrade -1

# Show current migration
db-current:
	uv run alembic current 

# Generate ER diagram
erd-generate:
	python scripts/generate_erd.py

# Generate documentation
docs-generate:
	make erd-generate
	mkdocs build 