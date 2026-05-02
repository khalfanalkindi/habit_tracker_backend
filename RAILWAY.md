# Railway (backend only)

Use this repo as its **own** Railway service. MySQL is a **separate** Railway plugin/service in the same project.

## Variables

| Name | Purpose |
|------|--------|
| `DATABASE_URL` | `mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE?charset=utf8mb4` — use Railway MySQL **private** host/port from the plugin variables. URL-encode special characters in the password. |
| `CORS_ORIGINS` | Your **frontend** public origin(s), comma-separated, e.g. `https://your-frontend.up.railway.app` |
| `PORT` | Set automatically by Railway; the Dockerfile respects it. |

## Service setup

1. New Railway service → deploy **this** GitHub repo (root = repo root, no subfolder if the repo contains only the backend).
2. If this repo is **only** `habit_tracker_backend` files at root, leave **Root Directory** empty. If the repo is a monorepo folder, set **Root Directory** to the backend folder name.
3. Add **MySQL** from Railway’s templates; copy its variables into `DATABASE_URL`.
4. **Networking** → generate a public URL for the API (needed for the browser / PWA).
5. After MySQL exists, **create tables once** (see **Database setup** below).

## Database setup (Railway MySQL)

Railway’s MySQL template **already creates a database** (see variable `MYSQLDATABASE`, often `railway`). You do **not** need `CREATE DATABASE` unless you want a second database name.

### A. Link the backend to MySQL

1. In the **MySQL** service → **Variables** — copy `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`.
2. In **habit_tracker_backend** → **Variables** → set **`DATABASE_URL`**:

   `mysql+pymysql://USER:PASSWORD@HOST:PORT/MYSQLDATABASE?charset=utf8mb4`

   Use the **private** `MYSQLHOST` / `MYSQLPORT` from Railway (service-to-service). If the password has `@`, `#`, `/`, etc., **URL-encode** it.
3. **Redeploy** the backend so it picks up `DATABASE_URL`.

### B. Create tables (one-time “migration”)

Until you add a migration runner (Alembic, etc.), create tables once:

**Option 1 — SQLAlchemy (no SQL files in the remote repo)**  
With `DATABASE_URL` set on the backend service:

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
