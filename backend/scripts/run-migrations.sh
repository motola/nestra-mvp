#!/bin/bash
set -e

# Run database migrations script
# This is called by GitHub Actions before deploying the backend

echo "Running database migrations on Fly.io..."

# Run migrations using flyctl machines
# The machine runs the production image and inherits environment from the app
flyctl machines run \
  --app nestra-mvp-api \
  --rm \
  -- registry.fly.io/nestra-mvp-api:latest \
  bash -c "cd /app && alembic upgrade head"

echo "Migrations completed successfully"
