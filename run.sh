#!/usr/bin/env bash

# uv run python flask_server/app.py

gunicorn -w 4 -b 0.0.0.0:5000 flask_server.app:app