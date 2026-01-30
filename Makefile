.PHONY: help venv install backend frontend test docker docker-up docker-down clean verify docs

help:
	@echo "Image to PDF Converter - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv          Create virtual environment"
	@echo "  make install       Install dependencies"
	@echo "  make verify        Verify installation"
	@echo ""
	@echo "Development:"
	@echo "  make backend       Run backend server"
	@echo "  make frontend      Run Kivy frontend"
	@echo "  make test          Run tests"
	@echo "  make test-coverage Run tests with coverage"
	@echo ""
	@echo "Docker:"
	@echo "  make docker        Build Docker image"
	@echo "  make docker-up     Start with Docker Compose"
	@echo "  make docker-down   Stop Docker containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         Remove cache and temp files"
	@echo "  make format        Format code"
	@echo "  make lint          Lint code"
	@echo "  make docs          Generate documentation"

venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install:
	pip install -r requirements.txt
	@echo "Dependencies installed successfully"

verify:
	python test_setup.py

backend:
	cd backend && python main.py

frontend:
	cd ui && python main.py

test:
	pytest backend/tests/ -v

test-coverage:
	pytest --cov=backend/services backend/tests/ --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

docker:
	docker build -t img-to-pdf .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "Cache and temp files cleaned"

format:
	black backend/
	isort backend/

lint:
	pylint backend/services/
	flake8 backend/

docs:
	@echo "Documentation:"
	@echo "  README.md        - Main project readme"
	@echo "  QUICKSTART.md    - Quick start guide"
	@echo "  README_DEV.md    - Development guide"
	@echo "  API.md           - API documentation"
	@echo ""
	@echo "To view: open [filename] in your browser"

.DEFAULT_GOAL := help
