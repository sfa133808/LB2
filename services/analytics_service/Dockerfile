# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
WORKDIR /build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8003

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv
COPY services/analytics_service/main.py ./main.py

USER appuser

EXPOSE 8003

CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8003}"]
