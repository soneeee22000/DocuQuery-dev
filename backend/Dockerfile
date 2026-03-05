FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml .python-version ./

# Install dependencies
RUN uv sync --no-dev --no-editable

# Copy application code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
