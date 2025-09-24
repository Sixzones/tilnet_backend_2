#!/bin/bash

# Railway startup script for Django
echo "Starting Tilnet Django Backend..."

# Activate virtual environment
source /app/venv/bin/activate

# Set default port if not provided
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Railway sets PORT dynamically, let's make sure it's available
if [ -z "$PORT" ]; then
    export PORT=8000
    echo "PORT not set, using default: $PORT"
else
    echo "PORT is set to: $PORT"
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migration failed, continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

# Test database connection before proceeding
echo "Testing database connection..."
python manage.py shell -c "
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Continuing without database operations...')
" || echo "Database connection test failed, continuing..."

# Create superuser if it doesn't exist (optional)
echo "Checking for superuser..."
python manage.py shell -c "
from django.db import connection
from django.contrib.auth import get_user_model
try:
    connection.ensure_connection()
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        print('No superuser found. Please create one manually.')
    else:
        print('Superuser exists.')
except Exception as e:
    print(f'Cannot check superuser due to database error: {e}')
" || echo "Superuser check failed, continuing..."

# Test Django app startup
echo "Testing Django app startup..."
python manage.py check --deploy || echo "Django check failed, but continuing..."

# Start the application
echo "Starting Gunicorn server on port $PORT..."
exec gunicorn tile_estimator.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --log-level info \
    --error-logfile - \
    --access-logfile - \
    --workers 2 \
    --timeout 120 \
    --preload
