#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Populate cities database with progress indicator
echo "Starting cities_light data population..."
python manage.py cities_light --progress
