.PHONY: lint test clean

lint:
		ruff format --exclude third_party
		ruff check --exclude third_party --fix --select I,E,W,F,B

test:
		pytest tests

clean:
		find app tests | grep __pycache__ | xargs rm -rf
