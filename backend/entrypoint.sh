#!/bin/bash
set -e

# Start the application
# Note: Database migrations are run separately via GitHub Actions before deployment
echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
