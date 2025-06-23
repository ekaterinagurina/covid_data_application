FROM python:3.11-slim

WORKDIR /app

COPY backend/app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/app /app
COPY backend/app/scripts /app/scripts
COPY .env /app/.env


ENV PYTHONPATH=/app

RUN chmod +x /app/scripts/entrypoint.sh /app/scripts/wait-for-it.sh

CMD ["sh", "/app/scripts/entrypoint.sh"]
