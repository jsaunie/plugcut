# Deploying Plugcut

Topology: the SPA is a static build on **Vercel**; the FastAPI API runs as a long-lived
container on **DigitalOcean App Platform** (the `Dockerfile` is portable to Railway / Fly /
Render / Cloud Run too); data lives in **Supabase Postgres**. The SPA calls same-origin
`/api/...`, and Vercel rewrites those to the API host, so there is no CORS in the browser
and the API URL stays hidden.

```
Browser ──▶ Vercel (static SPA)
              │  /api/*  (vercel.json rewrite)
              ▼
            API container (Dockerfile)  ──▶  Supabase Postgres
```

Local development is unchanged: SQLite + `uvicorn --reload` + `vite`. Postgres is only for
the deployed environment.

## 1. Database — Supabase

1. Create a project at https://supabase.com (note the database password).
2. Project settings ▸ Database ▸ **Connection string** ▸ choose the **Session pooler**
   (it supports the long-lived server and prepared statements; the transaction pooler also
   works because the engine sets `statement_cache_size=0`).
3. Take the URI and convert the scheme to asyncpg, i.e. start it with
   `postgresql+asyncpg://` instead of `postgresql://`. Example:

   ```
   postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   ```

   This is your `PLUGCUT_DATABASE_URL`.

The schema is created by Alembic on the API container's first boot (`alembic upgrade head`
runs from an empty database and builds every table). No SQL to run by hand.

## 2. API — DigitalOcean App Platform

The image is defined by `backend/Dockerfile` (migrates, then serves on `$PORT`; DO sets
`PORT=8080`). A ready App Spec lives at `.do/app.yaml`.

Always-on (no sleep), ~5 USD/month for the smallest instance (`basic-xxs`).

**Option A: from the App Spec (reproducible)**
```bash
doctl apps create --spec .do/app.yaml
# then set the secrets:
doctl apps update <app-id> --spec .do/app.yaml   # after editing CORS origin
```
Set `PLUGCUT_JWT_SECRET` and `PLUGCUT_DATABASE_URL` as encrypted env vars in the dashboard
(they are marked `type: SECRET` in the spec, so their values are not in git).

**Option B: from the dashboard (simplest)**
Apps ▸ Create App ▸ connect this GitHub repo ▸
- **Source Directory: `/backend`** (DO auto-detects the `Dockerfile` inside it)
- Resource type: **Web Service**, HTTP port **8080**, health check path **`/health`**
- Environment variables:
  - `PLUGCUT_JWT_SECRET` — `openssl rand -hex 32` (mark as Secret)
  - `PLUGCUT_DATABASE_URL` — the Supabase asyncpg URI from step 1 (mark as Secret)
  - `PLUGCUT_CORS_ORIGINS` — `["https://<your-app>.vercel.app"]`
  - `PLUGCUT_DEFAULT_LOCALE` — `fr`
  - `PLUGCUT_RESEND_API_KEY` / `PLUGCUT_EMAIL_FROM` — optional, for real reminder mail
  - `PLUGCUT_AUTO_CREATE_SCHEMA` — leave unset; the image forces it `false` (Alembic owns
    the schema)

Deploy. Note the app URL, e.g. `https://plugcut-api-xxxxx.ondigitalocean.app`.

The same `backend/Dockerfile` runs unchanged on other hosts if you ever switch:
- **Railway**: New Project ▸ Deploy from repo ▸ root `backend` ▸ same env vars (always-on,
  ~5 USD/mo).
- **Fly.io**: `cd backend && fly launch --dockerfile Dockerfile` ▸ `fly secrets set ...`
  (free tier can stay always-on).
- **Render**: Web Service ▸ Docker ▸ root `backend`. Note the free tier sleeps after 15 min
  (slow first request); a paid instance removes it.

## 3. SPA — Vercel

1. New Project ▸ import this repo.
2. **Root Directory: `frontend`** (Vercel reads `frontend/vercel.json`; framework, build
   command, and output dir are declared there).
3. Edit `frontend/vercel.json`: replace `REPLACE-WITH-YOUR-BACKEND-URL` with the API host
   from step 2 (no trailing slash), e.g. `https://plugcut-api.onrender.com`. Commit.
4. Deploy.

No frontend env vars are needed: the app calls relative `/api/v1/...`, and the rewrite
forwards those to the API.

## 4. Verify

- `https://<api-host>/health` returns `{"status":"ok"}`.
- `https://<app>.vercel.app` loads, registration/login works, a deal can be created.
- `https://<app>.vercel.app/api/v1/health` returns ok through the Vercel rewrite.

## Notes

- **Migrations** run automatically on every API deploy (`alembic upgrade head` in the
  container `CMD`). To add one: `uv run alembic revision --autogenerate -m "..."`, commit,
  redeploy.
- **Free-tier cold starts**: Render's free web service sleeps after inactivity; the first
  request wakes it (a few seconds). Fine for a portfolio demo; upgrade the instance to
  remove it.
- **Secrets** are never committed. `backend/.env.example` lists every variable.
