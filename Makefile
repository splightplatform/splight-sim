.PHONY: start stop clean clean-pyc clean-test traces check fix

start:
	@docker-compose -f docker-compose.yml up -d

stop:
	@docker-compose -f docker-compose.yml down

clean: clean-test clean-pyc stop
	@rm -rf .venv

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	find . -name '*.pytest_cache' -exec rm -rf {} +
	rm -rf .coverage_badge .coverage_report

traces:
	uv run traces/build.py

# CODE STYLE
check:
	uv run ruff format --check .
	uv run ruff check .

fix:
	uv run ruff format .
	uv run ruff check --fix .
