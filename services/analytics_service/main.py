import os
from datetime import datetime, timezone

from fastapi import FastAPI
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")
PORT = int(os.getenv("PORT", "8003"))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
app = FastAPI(title="analytics-service", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'todo',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        )


@app.get("/health")
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "service": "analytics-service",
        "port": PORT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/analytics/summary")
def summary() -> dict[str, int]:
    with engine.connect() as connection:
        users_count = connection.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        tasks_count = connection.execute(text("SELECT COUNT(*) FROM tasks")).scalar() or 0
        open_tasks = (
            connection.execute(text("SELECT COUNT(*) FROM tasks WHERE status <> 'done' ")).scalar() or 0
        )

    return {
        "users_total": int(users_count),
        "tasks_total": int(tasks_count),
        "open_tasks": int(open_tasks),
    }


@app.get("/")
def root() -> dict[str, str | int | dict]:
    h = health()
    h["endpoints"] = {
        "health": "/health",
        "analytics_summary": "/analytics/summary",
        "docs": "/docs",
    }
    return h
