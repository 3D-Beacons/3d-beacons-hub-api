default: test

.PHONY: sync test

sync:
	uv sync --extra dev

test: sync
	uv run pre-commit install
	uv run pre-commit run --all-files
	uv run coverage run --source=app/ -m pytest --junitxml=report.xml
	mkdir -p coverage
	uv run coverage xml -o coverage/cobertura-coverage.xml
	uv run coverage report -m
