import os
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://lb2user:lb2pass@db:5432/lb2app",
)
PORT = int(os.getenv("PORT", "8002"))

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TaskCreate(BaseModel):
    user_id: int
    title: str
    status: str = "todo"


app = FastAPI(title="tasks-service", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "service": "tasks-service",
        "port": PORT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/tasks")
def list_tasks() -> dict[str, list[dict]]:
    with Session(engine) as session:
        tasks = session.execute(select(Task).order_by(Task.id)).scalars().all()
        return {
            "items": [
                {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "status": task.status,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                }
                for task in tasks
            ]
        }


@app.post("/tasks")
def create_task(payload: TaskCreate) -> dict[str, int | str]:
    with Session(engine) as session:
        task = Task(user_id=payload.user_id, title=payload.title, status=payload.status)
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "status": task.status,
        }
