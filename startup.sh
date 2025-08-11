#!/bin/bash

# Create venv (if needed)
python3 -m venv antenv
source antenv/bin/activate

# Install requirements
pip install --no-cache-dir -r requirements.txt

# Run migrations directly via Python (works without FLASK_APP)
python3 - <<EOF
from flask import Flask
from app import app  # Import your Flask app instance
from flask_migrate import upgrade

with app.app_context():
    upgrade()
EOF

# Start Gunicorn server
gunicorn --bind=0.0.0.0 --timeout 600 app:app
