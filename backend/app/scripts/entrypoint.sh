#!/bin/sh

/app/scripts/wait-for-it.sh db:5432 --timeout=90 --strict -- echo "Database is up"

echo "Running database setup and data loading..."
python /app/database/setup_db.py

echo "Database setup and data loading completed successfully."

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000