#!/bin/bash

# Simple startup script for Railway
echo "Starting Tilnet Django Backend..."

# Activate virtual environment
source /app/venv/bin/activate

# Set port
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Basic Django check
echo "Running Django system check..."
python manage.py check || echo "Django check failed, continuing..."

# Start the application immediately
echo "Starting Gunicorn server on port $PORT..."
exec gunicorn tile_estimator.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --workers 1 \
    --timeout 60
