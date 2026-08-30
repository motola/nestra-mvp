#!/bin/bash
set -e

# Run database migrations script
# This is called by GitHub Actions before deploying the backend

echo "Running database migrations on Fly.io..."

# Run migrations using flyctl machines
# This executes the migration in a temporary machine with access to the production database
flyctl machines run \
  --app nestra-mvp-api \
  --yes \
  --wait-timeout 600 \
  --env DATABASE_URL="$DATABASE_URL" \
  -- bash -c "pip install -e . && alembic upgrade head"

echo "Migrations completed successfully"
