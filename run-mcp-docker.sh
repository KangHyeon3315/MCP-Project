#!/bin/bash

# Load .env file
set -a
source /Users/sonkanghyeon/Project/mcp-project/.env
set +a

# Run Docker container with environment variables
docker run -i --rm \
  -e DB_USER="${DB_USER}" \
  -e DB_PASSWORD="${DB_PASSWORD}" \
  -e DB_HOST="${DB_HOST}" \
  -e DB_PORT="${DB_PORT}" \
  -e DB_NAME="${DB_NAME}" \
  mcp-domain:latest
