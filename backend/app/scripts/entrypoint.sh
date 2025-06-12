#!/bin/sh

./wait-for-it.sh db:5432 -- echo "Database is up"

echo "Running database setup and data loading..."
python /app/database/database.py

echo "Database setup and data loading completed successfully."

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000