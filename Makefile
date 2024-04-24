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

clean-test: ## remove test and coverage artifacts
	find . -name '*.pytest_cache' -exec rm -rf {} +
	rm -rf .coverage_badge .coverage_report

# CODE STYLE
black: 
	black . --exclude '*/pydnp3/*'

isort:
	isort . --skip-glob '*/pydnp3/*'

flake8:
	sh -c "find . -type f -name '*.py' -not -path '*/pydnp3/*' -exec autoflake {} +"

format: flake8 isort black
