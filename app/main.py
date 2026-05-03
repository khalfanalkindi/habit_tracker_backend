"""FastAPI entrypoint for habit_tracker_backend."""

import os
from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.routers import auth, exercise_entries, food_log_entries, food_options, me, users_admin, weight_entries

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
    "Set the same `APP_TOKEN` on the server and `NEXT_PUBLIC_APP_TOKEN` on the frontend. "
    "Send `Authorization: Bearer <that value>` on every `/api` call. "
    "Send **`X-User-Id`** (user id from login) on `/api/me/*` so profile, food, exercise, and weight CRUD target that account. "
    "If omitted, `APP_USER_ID` or the only `users` row is used.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    # Railway PWA origins (https://….up.railway.app) — add more via CORS_ORIGINS if needed
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.up\.railway\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    # "*" headers + credentials is invalid for browsers; list what the PWA sends
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-User-Id"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(me.router, prefix="/api")
app.include_router(food_options.router, prefix="/api")
app.include_router(food_log_entries.router, prefix="/api")
app.include_router(exercise_entries.router, prefix="/api")
app.include_router(weight_entries.router, prefix="/api")
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
        "description": (
            "Same string as server env `APP_TOKEN`. For `/api/me/*` also send header "
            "`X-User-Id: <id>` from the login response so profile routes target that user."
        ),
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
