#!/bin/bash
set -e

# Start the application
# Note: Database migrations are run via Fly's release_command before this starts
echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
