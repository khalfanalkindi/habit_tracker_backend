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
5. After first deploy, create tables once: run `db/schema.sql` (full) or `db/init_tables.sql` against your MySQL database (TablePlus or Railway’s MySQL UI).

## Health check

Use path `/health` if Railway asks for a health check URL.
