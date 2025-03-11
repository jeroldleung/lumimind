.PHONY: lint

lint:
		ruff format --exclude third_party
		ruff check --exclude third_party --fix --select I,E,W,F,B

test:
		pytest tests
