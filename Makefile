.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

.PHONY: test
test:
	@pytest -c setup.cfg

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -delete
	find . -name '*.egg' -delete

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	## Files with tilde at the end of their name are backup files, created by some editors
	find . -name '*~' -delete
	find . -name '__pycache__' -delete

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-ignored
clean-ignored: ## remove all files, listed in .gitignore
	git clean -fxd

.PHONY: clean-ignored-with-git
clean-ignored-with-git: clean-ignored ## remove all files, listed in .gitignore, and .git directory itself
	rm -rf .git/
