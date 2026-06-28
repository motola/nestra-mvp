.PHONY: install dev test lint format type-check check types


dev:
	PYTHONPATH=src uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Regenerate the cross-language type contract: backend OpenAPI -> shared/api.ts.
types:
	python scripts/export_openapi.py
	npx --yes openapi-typescript ../shared/openapi.json -o ../shared/api.ts

test:
	PYTHONPATH=src python -m unittest discover -s . -p "test_*.py" -v

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src

check: lint type-check test
