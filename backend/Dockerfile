FROM python:3.11-slim

WORKDIR /app

COPY backend/app /app
COPY .env /app/.env

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

CMD ["sh", "/app/entrypoint.sh"]
