import os
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from fastapi import FastAPI

APP_NAME = os.getenv("APP_NAME", "StudyHub Gateway")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
TASKS_SERVICE_URL = os.getenv("TASKS_SERVICE_URL", "http://tasks-service:8002")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8003")

app = FastAPI(title=APP_NAME, version=APP_VERSION)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": f"{APP_NAME} is running",
        "project": "StudyHub microservices",
        "environment": APP_ENV,
        "version": APP_VERSION,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api-gateway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _proxy_request(method: str, base_url: str, path: str, payload: dict | None = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method, f"{base_url}{path}", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream service error: {exc}") from exc


@app.get("/users")
async def list_users() -> dict:
    return await _proxy_request("GET", USERS_SERVICE_URL, "/users")


@app.post("/users")
async def create_user(payload: dict) -> dict:
    return await _proxy_request("POST", USERS_SERVICE_URL, "/users", payload)


@app.get("/tasks")
async def list_tasks() -> dict:
    return await _proxy_request("GET", TASKS_SERVICE_URL, "/tasks")


@app.post("/tasks")
async def create_task(payload: dict) -> dict:
    return await _proxy_request("POST", TASKS_SERVICE_URL, "/tasks", payload)


@app.get("/analytics/summary")
async def analytics_summary() -> dict:
    return await _proxy_request("GET", ANALYTICS_SERVICE_URL, "/analytics/summary")
