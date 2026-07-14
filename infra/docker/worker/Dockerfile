FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/ingest/requirements.txt /app/services/ingest/requirements.txt
COPY services/worker/requirements.txt /app/services/worker/requirements.txt
COPY services/api/requirements.txt /app/services/api/requirements.txt
RUN pip install --no-cache-dir \
    -r /app/services/ingest/requirements.txt \
    -r /app/services/worker/requirements.txt \
    -r /app/services/api/requirements.txt

COPY packages/contracts/python /app/packages/contracts/python
COPY services/ingest /app/services/ingest
COPY services/worker /app/services/worker
COPY sources /app/sources

COPY services/api /app/services/api
ENV PYTHONPATH=/app/services/ingest:/app/services/worker:/app/services/api:/app/packages/contracts/python:/app/sources
WORKDIR /app/services/worker

CMD ["python", "-m", "tsubo_worker.main"]
