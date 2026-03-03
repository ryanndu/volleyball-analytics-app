#!/bin/bash
set -e

echo "Downloading database..."
python scripts/download_db.py

echo "Starting app..."
exec uvicorn app:app --host 0.0.0.0 --port 8000 --ws websockets