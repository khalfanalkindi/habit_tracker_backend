"""FastAPI entrypoint for habit_tracker_backend."""

import os
from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_ORIGINS: Sequence[str] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
)


def _cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    extra = [o.strip() for o in raw.split(",") if o.strip()]
    merged = list(DEFAULT_ORIGINS) + extra
    seen: set[str] = set()
    out: list[str] = []
    for o in merged:
        if o not in seen:
            seen.add(o)
            out.append(o)
    return out


app = FastAPI(
    title="Habit Tracker API",
    description="Backend for habit / food / exercise tracking",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "habit-tracker-backend", "docs": "/docs"}