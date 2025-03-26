ROOT_DIR := $(shell pwd)

.venv:
	python3 -m venv .venv
	@( \
		source .venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
	)

start:
	@docker-compose -f docker-compose.yml up -d

stop:
	@docker-compose -f docker-compose.yml down

clean: clean-test clean-pyc stop

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -rf .venv

clean-test: ## remove test and coverage artifacts
	find . -name '*.pytest_cache' -exec rm -rf {} +
	rm -rf .coverage_badge .coverage_report

# CODE STYLE
black: 
	black .

isort:
	isort .

flake8:
	sh -c "find . -type f -name '*.py' -exec autoflake {} +"

format: flake8 isort black

traces: .venv
	@. .venv/bin/activate; cd $(ROOT_DIR)/data/mqtt/traces && python3 $(ROOT_DIR)/scripts/trace_creator.py