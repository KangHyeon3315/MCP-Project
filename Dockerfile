FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2-binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first for layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev, no virtualenv inside container)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main --no-root

# Copy application code
COPY main.py ./
COPY src/ ./src/
COPY templates/ ./templates/

ENV UVICORN_PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port $UVICORN_PORT
