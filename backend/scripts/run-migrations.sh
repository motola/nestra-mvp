#!/bin/bash
set -e

# Run database migrations script
# This is called by GitHub Actions before deploying the backend

echo "Running database migrations on Fly.io..."

# Run migrations using flyctl machines
# The machine inherits environment from the app's configuration
flyctl machines run \
  --app nestra-mvp-api \
  --rm \
  --wait-timeout 600 \
  registry.fly.io/nestra-mvp-api:latest \
  bash -c "cd /app && pip install -e . && alembic upgrade head"

echo "Migrations completed successfully"
