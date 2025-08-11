#!/bin/bash

# Create venv (if needed)
if [ ! -d "antenv" ]; then
    python3 -m venv antenv
fi
source antenv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Start the app
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
