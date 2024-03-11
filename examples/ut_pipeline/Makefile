.PHONY: format lint test

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests/
integration_tests: TEST_FILE = tests/integration_tests/

# Run unit tests and generate a coverage report.
coverage:
	poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered \
		$(TEST_FILE)

PYTHON_FILES=.
MYPY_CACHE=.mypy_cache

format format_diff:
	@echo "Formatting code"
	poetry run ruff format $(PYTHON_FILES)
	poetry run ruff --select I --fix $(PYTHON_FILES)

lint lint_diff lint_package lint_tests:
	@echo "Running linter"
	poetry run ruff .
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff format $(PYTHON_FILES) --diff
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff --select I $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || mkdir -p $(MYPY_CACHE) && poetry run mypy $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

test tests integration_tests:
	@echo "Running unit tests && integration_tests"
	poetry run pytest $(TEST_FILE)

# Additional targets for setting up the environment, cleaning build artifacts, etc.
