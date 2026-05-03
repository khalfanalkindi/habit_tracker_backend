# Railway (backend only)

Use this repo as its **own** Railway service. MySQL is a **separate** Railway plugin/service in the same project.

## Variables

| Name | Purpose |
|------|--------|
| `DATABASE_URL` | Optional if MySQL vars are on the service (see below). When set: `mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE?charset=utf8mb4`. Railway’s `mysql://` URL is accepted and normalized at runtime. URL-encode special characters in the password. |
| `MYSQLHOST`, `MYSQLUSER`, … | When **`DATABASE_URL` is unset**, the API builds the URL from `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLPORT`, `MYSQLDATABASE` (Railway’s MySQL plugin names). Add them via **Variables → Reference** from the MySQL service onto the backend. |
| `CORS_ORIGINS` | Extra allowed browser origins (comma-separated). Defaults already include `localhost` and **`https://*.up.railway.app`** for Railway frontends. Add your domain here if you use a custom host. |
| `PORT` | Set automatically by Railway; the Dockerfile respects it. |
| `APP_TOKEN` | **You add this** — one shared secret. Every `/api` request must send `Authorization: Bearer <APP_TOKEN>`. Use the **same** value as frontend `NEXT_PUBLIC_APP_TOKEN`. Leave **empty** only for local dev (no bearer check). |
| `APP_USER_ID` | Optional fallback when the client does **not** send `X-User-Id`. If you have several users, the PWA sends **`X-User-Id`** (from login) on `/api/me/*` so profile CRUD hits the right row; you can still set `APP_USER_ID` for tools like curl without that header. |

The **“8 variables added by Railway”** block (`RAILWAY_PUBLIC_DOMAIN`, etc.) is only Railway metadata.

## Service setup

1. New Railway service → deploy **this** GitHub repo (root = repo root, no subfolder if the repo contains only the backend).
2. If this repo is **only** `habit_tracker_backend` files at root, leave **Root Directory** empty. If the repo is a monorepo folder, set **Root Directory** to the backend folder name.
3. Add **MySQL** from Railway’s templates; either **reference** its `MYSQL*` variables onto the backend service or set a single `DATABASE_URL`.
4. **Networking** → generate a public URL for the API (needed for the browser / PWA).
5. After MySQL exists, **create tables once** (see **Database setup** below).

## Database setup (Railway MySQL)

Railway’s MySQL template **already creates a database** (see variable `MYSQLDATABASE`, often `railway`). You do **not** need `CREATE DATABASE` unless you want a second database name.

### A. Link the backend to MySQL

1. In **habit_tracker_backend** → **Variables** → **+ New Variable** → **Add Reference** (or equivalent) and pull **`MYSQLHOST`**, **`MYSQLUSER`**, **`MYSQLPASSWORD`**, **`MYSQLPORT`**, **`MYSQLDATABASE`** from the MySQL service. The API will build `mysql+pymysql://…` automatically; you do **not** need `DATABASE_URL` unless you prefer one variable.

2. **Alternatively**, set **`DATABASE_URL`** manually:

   `mysql+pymysql://USER:PASSWORD@HOST:PORT/MYSQLDATABASE?charset=utf8mb4`

   Use the **private** `MYSQLHOST` / `MYSQLPORT` from Railway (service-to-service). If the password has `@`, `#`, `/`, etc., **URL-encode** it.

3. **Redeploy** the backend so it picks up the new variables.

### B. Create tables (one-time “migration”)

Until you add a migration runner (Alembic, etc.), create tables once:

**Option 1 — SQLAlchemy (no SQL files in the remote repo)**  
With `DATABASE_URL` or referenced `MYSQL*` variables on the backend service:

```bash
python3 -m app.db.init_db
```

That creates tables from `app/db/models.py` (same shapes as your local `db/` SQL, which is **gitignored** and not pushed).

**Option 2 — TablePlus / mysql client**  
Use your **local** copy of `db/init_tables.sql` or `db/schema.sql` (kept on your machine only) against the Railway database.

**If the database already had an older `users` shape**, use your local **`db/alter_migrate_full_frontend_alignment.sql`** (or the smaller resume scripts in `db/`) once after a backup.

After tables exist, your API can use the DB once you add routes that use SQLAlchemy.

## Health check

Use path `/health` if Railway asks for a health check URL.
