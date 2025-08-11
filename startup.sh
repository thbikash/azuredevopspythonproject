#!/bin/bash

# Create venv (if needed)
if [ ! -d "antenv" ]; then
    python3 -m venv antenv
fi
source antenv/bin/activate

# Upgrade pip (optional but good practice)
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Ensure flask-migrate is installed
if ! pip show flask-migrate > /dev/null 2>&1; then
    echo "Installing flask-migrate..."
    pip install flask-migrate
fi

# Run migrations
flask db upgrade || echo "⚠️ Migration failed — continuing startup"

# Start the app
gunicorn --bind=0.0.0.0 --timeout 600 app:app
