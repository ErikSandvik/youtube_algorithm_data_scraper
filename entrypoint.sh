#!/bin/bash
set -e


echo "Running database migrations..."
alembic upgrade head

echo "Starting the main application..."
python -u app/main.py

