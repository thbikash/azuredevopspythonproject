#!/bin/bash

# Create venv (if needed)
python3 -m venv antenv
source antenv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run your app
gunicorn --bind=0.0.0.0 --timeout 600 app:app
