FROM python:3.11-slim

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

CMD ["sh", "/app/entrypoint.sh"]
