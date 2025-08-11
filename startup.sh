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

# Set the Flask app entry point (adjust to your actual app file or package)
export FLASK_APP=app.py  # or 'app' if it's a package with __init__.py

# Run migrations
flask db upgrade || echo "⚠️ Migration failed — continuing startup"

# Start the app
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
