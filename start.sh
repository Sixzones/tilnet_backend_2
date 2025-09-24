#!/bin/bash

# Railway startup script for Django
echo "Starting Tilnet Django Backend..."

# Activate virtual environment
source /app/venv/bin/activate

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually.')
else:
    print('Superuser exists.')
"

# Start the application
echo "Starting Gunicorn server..."
echo "Using PORT: ${PORT:-8000}"
exec gunicorn tile_estimator.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --log-level info \
    --error-logfile - \
    --access-logfile - \
    --workers 2 \
    --timeout 120
