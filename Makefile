# Makefile for macOS development

.PHONY: setup install run-api run-cli test clean help

# Setup virtual environment and install dependencies
setup:
	python3 -m venv venv
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt

# Install/update dependencies
install:
	source venv/bin/activate && pip install -r requirements.txt

# Run FastAPI development server
run-api:
	source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

# Run CLI commands
run-cli:
	source venv/bin/activate && python -m app.cli

# Test CLI with sample CSV
test-cli:
	source venv/bin/activate && python -m app.cli create --file sample.csv

# Run tests
test:
	source venv/bin/activate && pytest -v

# Test services
test-services:
	source venv/bin/activate && python -m app.cli test

# Clean up
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Show project structure
tree:
	tree -I 'venv|__pycache__|*.pyc|.git'

# Show help
help:
	@echo "Available commands:"
	@echo "  make setup        - Create virtual environment and install dependencies"
	@echo "  make install      - Install/update dependencies"
	@echo "  make run-api      - Start FastAPI development server"
	@echo "  make run-cli      - Show CLI help"
	@echo "  make test-cli     - Test CLI with sample CSV"
	@echo "  make test         - Run tests"
	@echo "  make test-services - Test all services"
	@echo "  make clean        - Clean up Python cache files"
	@echo "  make tree         - Show project structure"
	@echo "  make help         - Show this help"
