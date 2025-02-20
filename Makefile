.PHONY: lint

lint:
		@ruff format .
		@ruff check . --fix --select I,E,F,B