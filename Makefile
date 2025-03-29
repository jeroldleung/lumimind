.PHONY: lint test clean

lint:
		uv run ruff format
		uv run ruff check --fix

test:
		uv run pytest tests

clean:
		find app tests | grep __pycache__ | xargs rm -rf
