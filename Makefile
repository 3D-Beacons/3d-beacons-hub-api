default: test

test:
	pip install -r dev-requirements.txt
	pip install -r requirements.txt
	pre-commit install && pre-commit run --all
	coverage run --source=app/ -m pytest --junitxml=report.xml
	coverage xml -o coverage/cobertura-coverage.xml
	coverage report -m
