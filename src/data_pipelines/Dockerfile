FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app/src/data-pipelines/

CMD python /app/src/data-pipelines/sync_raw_from_s3.py && \
    python /app/src/data-pipelines/pipeline.py && \
    python /app/src/data-pipelines/load_to_postgres.py
