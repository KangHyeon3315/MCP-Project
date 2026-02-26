FROM python:3.13-slim

WORKDIR /app

# Install poetry
RUN pip install poetry==2.1.3

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY src ./src
COPY mcp_server.py .

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Run the MCP server
CMD ["python", "mcp_server.py"]
