#!/bin/bash

# Wait for Redis to be ready
echo "Waiting for Redis..."
until nc -z redis 6379; do
  sleep 1
done
echo "Redis is up!"

# Run migrations
python manage.py migrate
python manage.py migrate video

# Start Celery worker
celery -A fampay worker --loglevel=info &

# Start Celery beat
celery -A fampay beat --loglevel=info &

# Start Django server
python manage.py runserver 0.0.0.0:8000