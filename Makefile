.PHONY: help install install-dev test test-all lint format type-check clean build upload docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package for production
	pip install -e .

install-dev:  ## Install package for development
	pip install -e ".[dev]"
	pip install -r requirements/dev.txt
	pre-commit install

install-test:  ## Install package for testing
	pip install -e .
	pip install -r requirements/test.txt

test:  ## Run unit tests
	pytest tests/ -v --cov=pytubesearch --cov-report=term-missing

test-all:  ## Run all tests including integration tests
	pytest tests/ -v --cov=pytubesearch --cov-report=term-missing -m "not integration"
	pytest tests/ -v -m "integration" --tb=short

test-integration:  ## Run only integration tests
	pytest tests/ -v -m "integration"

lint:  ## Run linting checks
	flake8 pytubesearch tests
	black --check pytubesearch tests
	isort --check-only pytubesearch tests

format:  ## Format code
	black pytubesearch tests
	isort pytubesearch tests

type-check:  ## Run type checking
	mypy pytubesearch

security:  ## Run security checks
	bandit -r pytubesearch
	safety check

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

upload-test:  ## Upload to Test PyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

docs:  ## Generate documentation
	sphinx-build -b html docs/ docs/_build/html

check:  ## Run all checks (lint, type-check, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

ci:  ## Run CI pipeline locally
	$(MAKE) clean
	$(MAKE) install-test
	$(MAKE) check
	$(MAKE) security