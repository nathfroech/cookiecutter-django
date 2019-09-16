.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

.PHONY: test
test:
	@pytest -c setup.cfg
