.PHONY: format lint test

PYTHON_FILES=.

format:
	@echo "Formatting code"
	poetry run ruff format $(PYTHON_FILES)
	poetry run ruff --select I --fix $(PYTHON_FILES)

lint:
	@echo "Linting code"
	poetry run flake8 ut_sample tests
	poetry run mypy ut_sample tests
	@echo "Checking for proper imports"
	./scripts/check_imports.py
	./scripts/lint_imports.sh
	./scripts/check_pydantic.sh

test:
	@echo "Running unit tests"
	poetry run pytest

# Additional targets for setting up the environment, cleaning build artifacts, etc.
