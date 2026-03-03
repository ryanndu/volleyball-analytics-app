#!/bin/bash
set -e

echo "Downloading database..."
python scripts/download_db.py

echo "Starting app..."
exec shiny run app.py --host 0.0.0.0 --port 8000