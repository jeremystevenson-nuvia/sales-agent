FROM python:3.11-slim as base

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./core ./core
COPY ./ai ./ai
COPY ./tests ./tests
COPY ./README.md ./

# --- Test stage ---
FROM base as test
CMD ["pytest", "tests/"]

# --- Runtime stage (final) ---
FROM base as runtime
EXPOSE 8000
CMD ["uvicorn", "core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
