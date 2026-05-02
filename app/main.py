"""FastAPI entrypoint for habit_tracker_backend."""

import os
from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.routers import auth, me, users_admin

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
    description="Backend for habit / food / exercise tracking. "
    "Call `POST /api/auth/login` with no auth, then send `Authorization: Bearer <access_token>` on other `/api` routes.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(me.router, prefix="/api")
app.include_router(users_admin.router, prefix="/api")


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schemes = openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Paste the `access_token` from `POST /api/auth/login` (Swagger adds `Bearer `). Login itself needs no token.",
    }
    for path, path_item in openapi_schema.get("paths", {}).items():
        if not path.startswith("/api"):
            continue
        for method, op in path_item.items():
            if method in ("get", "post", "put", "delete", "patch") and isinstance(op, dict):
                if path == "/api/auth/login" and method == "post":
                    op["security"] = []
                else:
                    op["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "habit-tracker-backend", "docs": "/docs"}
