#!/bin/bash
set -e

# Run database migrations script
# This is called by GitHub Actions before deploying the backend

echo "Running database migrations on Fly.io..."

# Run migrations using flyctl machines
# The machine inherits all secrets and environment variables from the nestra-mvp-api app
flyctl machines run \
  --app nestra-mvp-api \
  --yes \
  --wait-timeout 600 \
  --inherit-env \
  -- bash -c "pip install -e . && alembic upgrade head"

echo "Migrations completed successfully"
