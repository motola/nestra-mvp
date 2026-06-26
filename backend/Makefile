.PHONY: install dev test lint format type-check check


dev:
	PYTHONPATH=src uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=src DEBUG=True python -m unittest discover -s . -p "test_*.py" -v

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src

check: lint type-check test
