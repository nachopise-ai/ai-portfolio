FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAG_DB_PATH=/app/var/rag.sqlite3

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY data ./data

RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/var \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
CMD ["python", "-m", "app.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]
