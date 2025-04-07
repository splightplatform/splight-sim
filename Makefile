ROOT_DIR := $(shell pwd)

venv:
	@python3 -m venv venv
	@( \
		source venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
	)
	@clear

start:
	@docker-compose -f docker-compose.yml up -d

stop:
	@docker-compose -f docker-compose.yml down

clean: clean-test clean-pyc stop
	@rm -rf venv

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	find . -name '*.pytest_cache' -exec rm -rf {} +
	rm -rf .coverage_badge .coverage_report

# CODE STYLE
black: venv
	@. venv/bin/activate; black .

isort: venv
	@. venv/bin/activate; isort .

flake8: venv
	@. venv/bin/activate; sh -c "find . -path  ./venv -prune -o -type f -name '*.py' -exec flake8 {} +"

format: isort black flake8

traces: venv
	@. venv/bin/activate; cd $(ROOT_DIR)/data/mqtt/traces && python3 $(ROOT_DIR)/scripts/trace_creator.py