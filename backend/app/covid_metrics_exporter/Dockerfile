FROM python:3.11-slim

WORKDIR /app

COPY exporter.py .

RUN pip install pandas prometheus_client

ENV COVID_DATA_DIR=/app/data

CMD ["python", "exporter.py"]
