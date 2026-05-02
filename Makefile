.PHONY: install dev dev-services dev-backend dev-frontend \
        test test-backend test-frontend test-e2e \
        lint lint-backend lint-frontend \
        format format-backend format-frontend \
        type-check type-check-backend type-check-frontend \
        clean

# ── Setup ──────────────────────────────────────────────────────────────────────

install:
	pip install pre-commit
	pre-commit install --hook-type pre-commit --hook-type commit-msg
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

# ── Local development ──────────────────────────────────────────────────────────

## Start everything (requires Dockerfiles from Batch 3 & 4)
dev:
	docker compose --profile app up --watch

## Start only Postgres + Redis (available now)
dev-services:
	docker compose up -d

## Start backend with hot reload (after: make dev-services)
dev-backend:
	cd backend && uvicorn alphacon.main:app --reload --host 0.0.0.0 --port 8000

## Start frontend with hot reload (after: make dev-services)
dev-frontend:
	cd frontend && npm run dev

# ── Tests ──────────────────────────────────────────────────────────────────────

test: test-backend test-frontend

test-backend:
	cd backend && python -m unittest discover -s . -p "test_*.py" -v

test-frontend:
	cd frontend && npm run test

test-e2e:
	cd frontend && npx playwright test

# ── Lint ───────────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check .

lint-frontend:
	cd frontend && npm run lint

# ── Format ─────────────────────────────────────────────────────────────────────

format: format-backend format-frontend

format-backend:
	cd backend && ruff format .

format-frontend:
	cd frontend && npm run format

# ── Type checking ──────────────────────────────────────────────────────────────

type-check: type-check-backend type-check-frontend

type-check-backend:
	cd backend && mypy alphacon

type-check-frontend:
	cd frontend && npm run type-check

# ── Cleanup ────────────────────────────────────────────────────────────────────

clean:
	docker compose --profile app down -v
