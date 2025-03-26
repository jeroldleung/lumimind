.PHONY: lint test clean

lint:
		ruff format
		ruff check --fix

test:
		pytest tests

clean:
		find app tests | grep __pycache__ | xargs rm -rf
