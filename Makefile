.PHONY: help install dev-install migrate test test-cov lint format check clean run shell

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make dev-install  - Install development dependencies"
	@echo "  make migrate      - Run database migrations"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make check        - Run Django system check"
	@echo "  make clean        - Clean temporary files"
	@echo "  make run          - Run development server"
	@echo "  make shell        - Open Django shell"

install:
	uv pip install -e .

dev-install:
	uv pip install -e ".[dev]"
	pre-commit install

migrate:
	cd src && python manage.py makemigrations
	cd src && python manage.py migrate

test:
	pytest

test-cov:
	pytest --cov --cov-report=html

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

check:
	cd src && python manage.py check
	cd src && python manage.py makemigrations --check --dry-run

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

run:
	cd src && python manage.py runserver

shell:
	cd src && python manage.py shell_plus
