.PHONY: update_requirements
update_requirements:
	bash helpers/update_requirements.sh

.PHONY: test
test:
	@pytest -c setup.cfg

.PHONY: coverage
coverage:
	@pytest -c setup.cfg --cov-config setup.cfg -s --cov-report term --cov {{ cookiecutter.project_slug }}
