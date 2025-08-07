#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --chdir /home/site/wwwroot/task-manager app:app
