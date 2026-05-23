import os
from datetime import datetime, timezone

from fastapi import FastAPI

APP_NAME = os.getenv("APP_NAME", "LB2 Render Demo")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": f"{APP_NAME} is running",
        "environment": APP_ENV,
        "version": APP_VERSION,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
