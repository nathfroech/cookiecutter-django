.PHONY: update_requirements
update_requirements:
	bash helpers/update_requirements.sh

.PHONY: lint
lint:
	@pre-commit run --all-files

.PHONY: test
test:
	@export PROJECT_ENVIRONMENT = test
	@pytest -c setup.cfg

.PHONY: coverage
coverage:
	@export PROJECT_ENVIRONMENT = test
	@pytest -c setup.cfg --cov-config setup.cfg -s --cov-report term --cov .

.PHONY: env_file
env_file:
	@python helpers/generate_env_file.py
