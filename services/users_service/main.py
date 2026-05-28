import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://lb2user:lb2pass@db:5432/lb2app",
)
PORT = int(os.getenv("PORT", "8001"))

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserCreate(BaseModel):
    name: str
    email: EmailStr


app = FastAPI(title="users-service", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "service": "users-service",
        "port": PORT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/users")
def list_users() -> dict[str, list[dict]]:
    with Session(engine) as session:
        users = session.execute(select(User).order_by(User.id)).scalars().all()
        return {
            "items": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                }
                for user in users
            ]
        }


@app.post("/users")
def create_user(payload: UserCreate) -> dict[str, int | str]:
    with Session(engine) as session:
        existing = session.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Email already exists")

        user = User(name=payload.name, email=payload.email)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {"id": user.id, "name": user.name, "email": user.email}



@app.get("/")
def root() -> dict[str, str | int | dict]:
    h = health()
    h["endpoints"] = {
        "health": "/health",
        "users": "/users",
        "docs": "/docs",
    }
    return h
