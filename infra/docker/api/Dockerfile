FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt /app/services/api/requirements.txt
RUN pip install --no-cache-dir -r /app/services/api/requirements.txt

COPY packages/contracts/python /app/packages/contracts/python
COPY services/api /app/services/api
COPY sources /app/sources

ENV PYTHONPATH=/app/services/api:/app/packages/contracts/python:/app/sources
WORKDIR /app/services/api

CMD ["uvicorn", "tsubo_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
