.PHONY: help install test coverage run docker-build docker-up docker-down docker-logs clean lint

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make run           - Run bot locally (requires YT_TRANSCRIPT_* env vars)"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - Show Docker container logs"
	@echo "  make clean         - Clean temporary files"
	@echo "  make lint          - Run basic syntax check"

install:
	pip install -r requirements.txt

test:
	python -m pytest -v

coverage:
	python -m pytest --cov=src --cov-report=term-missing --cov-report=html

run:
	@python -c "import os, sys; \
	os.environ['TELEGRAM_BOT_TOKEN'] = os.getenv('YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN', ''); \
	os.environ['YOUTUBE_API_KEY'] = os.getenv('YT_TRANSCRIPT_YOUTUBE_API_KEY', ''); \
	os.environ['OPENAI_API_KEY'] = os.getenv('YT_TRANSCRIPT_OPENAI_API_KEY', ''); \
	os.environ['DATABASE_URL'] = os.getenv('YT_TRANSCRIPT_DATABASE_URL', 'sqlite:///./data/bot.db'); \
	os.environ['LOG_LEVEL'] = os.getenv('YT_TRANSCRIPT_LOG_LEVEL', 'INFO'); \
	import runpy; runpy.run_module('src.bot', run_name='__main__')"

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f bot

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

lint:
	@echo "Running Python syntax check..."
	@python -m py_compile src/*.py tests/*.py
	@echo "✓ All files passed syntax check"
