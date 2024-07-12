#!/usr/bin/env bash
echo "Building project packages..."
pip install -r requirements.txt

echo "Migrating Database..."
python manage.py makemigrations -noinput
python manage.py migrate -noinput

echo "Collecting static files..."
python manage.py collectstatic -noinput