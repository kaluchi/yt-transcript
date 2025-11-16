.PHONY: help install test coverage run docker-build docker-up docker-down clean lint format

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make run          - Run bot locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make clean        - Clean temporary files"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"

install:
	pip install -r requirements.txt

test:
	pytest -v

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html

run:
	python -m src.bot

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

lint:
	@echo "Running basic Python syntax check..."
	python -m py_compile src/*.py

format:
	@echo "For formatting, install black: pip install black"
	@echo "Then run: black src/ tests/"
