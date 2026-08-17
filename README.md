# OpenSignal

Signal-based demand generation for GTM-360. Detect buying intent, score target accounts with Claude, and run personalized outreach campaigns — all on free tiers.

## Architecture

| Layer | Tech | Deploy |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | Cloudflare Pages (`frontend/build`) |
| API | Python 3.12 + FastAPI | Render (free tier) |
| Database | PostgreSQL | Supabase |
| Queues / rate limit | Redis | Upstash (optional) |
| AI | AWS Bedrock Claude | AWS |
| Email | Mailgun / SendGrid | — |
| Data sources | Apollo, Hunter, NewsAPI, GA4, SEC EDGAR | — |
| CRM sync | HubSpot, Salesforce | — |
| CI/CD | GitHub Actions | — |

## Repository layout

```
backend/             FastAPI application (auth, signals, campaigns, email, CRM, analytics)
frontend/            React + Vite SPA (builds to frontend/build for Cloudflare Pages)
supabase/            SQL migrations (schema, RLS, triggers)
.github/workflows/   Deploy pipelines (Cloudflare Pages + Render)
docker-compose.yml   Local stack (postgres, redis, backend, worker)
render.yaml          Render blueprint
```

## Backend

### Local setup

```bash
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
venv/bin/activate                  # macOS / Linux
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and set at least:

```env
ENVIRONMENT=development
JWT_SECRET=change-me
ENCRYPTION_KEY=<base64 32-byte key>   # python -c "import base64,os;print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

Optional connections (all fall back to no-op / env defaults when unset):

```env
DATABASE_URL=postgresql+asyncpg://...   # defaults to local sqlite when empty
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
APOLLO_API_KEY=...
HUNTER_API_KEY=...
NEWSAPI_KEY=...
MAILGUN_API_KEY=...
MAILGUN_DOMAIN=...
SENDGRID_API_KEY=...
HUBSPOT_API_KEY=...
SALESFORCE_CLIENT_ID=...
SALESFORCE_CLIENT_SECRET=...
SALESFORCE_USERNAME=...
SALESFORCE_PASSWORD=...
GA4_PROPERTY_ID=...
GA4_SERVICE_ACCOUNT_JSON=...
AWS_ACCESS_KEY_ID=...                # Bedrock Claude
AWS_SECRET_ACCESS_KEY=...
BEDROCK_REGION=...
REDIS_URL=...
SENTRY_DSN=...
```

Run locally:

```bash
uvicorn main:app --reload
```

Interactive docs at http://localhost:8000/docs.

### Tests

```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
```

Tests run against SQLite and never hit external APIs (service keys are cleared in `tests/conftest.py`).

### Seed demo data

```bash
.\venv\Scripts\python.exe -m scripts.seed_db
```

## Frontend

### Local setup

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000, proxies /api -> localhost:8000
```

Copy `frontend/.env.example` to `frontend/.env.local` and configure:

```env
VITE_API_URL=                      # leave empty to use the Vite proxy in dev
VITE_SUPABASE_URL=                 # optional; leave empty to use backend email/password auth
VITE_SUPABASE_ANON_KEY=
```

### Build & tests

```bash
npm run build      # outputs to frontend/build (Cloudflare Pages directory)
npm test
```

## Database (Supabase)

Apply the schema manually:

```sql
-- psql $DATABASE_URL -f supabase/migrations/001_init.sql
```

or run the Alembic migration:

```bash
cd backend
.\venv\Scripts\python.exe -m alembic upgrade head
```

## Deploying

- **Frontend**: push to `main` → GitHub Actions builds `frontend/build` and deploys to Cloudflare Pages (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` secrets).
- **Backend**: push to `main` → GitHub Actions runs backend tests, then triggers a Render deploy (`RENDER_SERVICE_ID`, `RENDER_DEPLOY_KEY` secrets). Alternatively use `render.yaml` ("Blueprint" from the dashboard).
- **Celery worker**: `celery -A app.tasks.celery_app worker --loglevel=info` (included in docker-compose and render.yaml).
- **Local stack**: `docker compose up` (postgres + redis + backend + worker).

## Auth

- With `SUPABASE_URL`/`SUPABASE_ANON_KEY` configured: Supabase handles user management; the frontend exchanges the Supabase session for an OpenSignal JWT at `/api/v1/auth/exchange`.
- Without them: the backend's built-in email/password auth (`/api/v1/auth/signup`, `/api/v1/auth/login`) issues JWTs directly.

## Security notes

- User service credentials are AES-256-GCM encrypted at rest (`ENCRYPTION_KEY`).
- Passwords are hashed with PBKDF2-SHA256 (never stored in plaintext).
- Rate limiting: 300 req/min/IP via Upstash Redis (in-memory fallback).
- JWT access tokens expire (default 24h); use Supabase refresh tokens in hosted mode.