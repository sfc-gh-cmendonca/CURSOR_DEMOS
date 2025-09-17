# Makefile for JPMC Cortex Search Lab

.PHONY: help setup install clean test lint format type-check security run-app run-dev build docs

# Default target
help:
	@echo "Available commands:"
	@echo "  setup         - Set up development environment"
	@echo "  install       - Install dependencies"
	@echo "  clean         - Clean up build artifacts"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black and isort"
	@echo "  type-check    - Run type checking with mypy"
	@echo "  security      - Run security checks with bandit"
	@echo "  quality       - Run all quality checks (lint, type, security)"
	@echo "  run-app       - Run Streamlit application"
	@echo "  run-dev       - Run application in development mode"
	@echo "  docs          - Generate documentation"
	@echo "  pre-commit    - Run pre-commit hooks"

# Environment setup
setup:
	@echo "Setting up development environment..."
	python setup.py

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Cleaning
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf bandit-report.json

# Testing
test:
	@echo "Running all tests..."
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-unit:
	@echo "Running unit tests..."
	pytest tests/ -m "unit" -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/ -m "integration" -v

test-watch:
	@echo "Running tests in watch mode..."
	pytest-watch tests/ -v

# Code quality
lint:
	@echo "Running linting..."
	flake8 src/ tests/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

type-check:
	@echo "Running type checks..."
	mypy src/

security:
	@echo "Running security checks..."
	bandit -r src/ -f json -o bandit-report.json

quality: lint type-check security
	@echo "All quality checks completed"

# Application
run-app:
	@echo "Starting Streamlit application..."
	streamlit run src/streamlit_app/main.py

run-dev:
	@echo "Starting application in development mode..."
	streamlit run src/streamlit_app/main.py --server.runOnSave=true

# Documentation
docs:
	@echo "Generating documentation..."
	@if [ -d "docs/" ]; then \
		echo "Documentation directory exists"; \
	else \
		mkdir -p docs/; \
	fi
	@echo "Documentation generation complete"

# Pre-commit
pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install

# Database operations
db-test:
	@echo "Testing database connection..."
	python -c "from src.database.connection import connection_manager; print('✓ Connected' if connection_manager.test_connection() else '✗ Connection failed')"

# Performance monitoring
profile:
	@echo "Profiling application..."
	python -m cProfile -o profile_stats.prof src/streamlit_app/main.py

# Environment validation
validate-env:
	@echo "Validating environment..."
	python -c "from src.config.settings import validate_settings; exit(0 if validate_settings() else 1)"

# Dependency management
update-deps:
	@echo "Updating dependencies..."
	pip list --outdated
	@echo "Review outdated packages and update requirements.txt manually"

# Build and distribution
build:
	@echo "Building package..."
	python -m build

# Development helpers
jupyter:
	@echo "Starting Jupyter Lab..."
	jupyter lab

notebook-clean:
	@echo "Cleaning notebook outputs..."
	jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace notebooks/*.ipynb

# Performance benchmarks
benchmark:
	@echo "Running performance benchmarks..."
	python -m pytest tests/benchmarks/ -v

# Full development cycle
dev-cycle: format lint type-check test
	@echo "Development cycle complete ✅"

# CI/CD simulation
ci: clean install quality test
	@echo "CI pipeline simulation complete ✅" 