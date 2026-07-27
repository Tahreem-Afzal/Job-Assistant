# Pathfinder — AI Job & Scholarship Assistant (v1)

A working MVP: React + TypeScript frontend, FastAPI backend, PostgreSQL database,
job search aggregated across Adzuna + Jooble (with graceful fallback if one is
unavailable or not configured), AI-powered match scoring, and a cover letter
generator. LinkedIn/Indeed are intentionally **not** integrated yet — see the
"Adding LinkedIn later" note at the bottom.

## What's built

- **Auth**: register/login with JWT, bcrypt-hashed passwords
- **Profile**: skills, preferred titles/countries, remote preference, visa
  needs, resume text — all feed into matching
- **Job search**: `/jobs/search` queries Adzuna and Jooble concurrently,
  merges + dedupes results, scores each against the user's profile
- **Saved jobs**: save, track status (saved → applied → interview → offer /
  rejected), remove
- **AI layer**: currently a transparent keyword-overlap stub (works with zero
  API keys) so the whole app is demoable immediately. One function
  (`_call_llm` in `backend/app/services/ai_matcher.py`) is the single place to
  wire in Groq/OpenAI later — nothing else needs to change.
- **Cover letter generator**: same stub pattern, upgrades automatically once
  an LLM key is added

## Project structure

```
backend/
  app/
    main.py          # FastAPI app, CORS, router registration
    config.py         # env-based settings
    database.py         # SQLAlchemy engine/session
    models.py            # User, Profile, SavedJob
    schemas.py             # Pydantic request/response models
    auth.py                  # JWT + password hashing
    routers/                  # auth, profile, jobs, saved, ai
    services/                  # adzuna_client, jooble_client, job_aggregator, ai_matcher
  requirements.txt
  .env.example
frontend/
  src/
    api/client.ts        # typed API wrapper (axios)
    context/AuthContext.tsx
    components/           # Navbar, JobCard (with match-score compass)
    pages/                  # Login, Register, Search, Saved, Profile, Resume
    styles.css                # design tokens (navy/gold "Pathfinder" theme)
  package.json
```

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set DATABASE_URL to your Postgres instance
# (or use sqlite:///./dev.db for zero-setup local testing)
uvicorn app.main:app --reload
```

API docs at `http://localhost:8000/docs` once running.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App at `http://localhost:5173`.

### 3. Get free API keys (optional but needed for real job results)

- **Adzuna**: https://developer.adzuna.com/ → free app_id + app_key
- **Jooble**: https://jooble.org/api/about → free API key

Without either key, `/jobs/search` still returns `200` with an empty list
(graceful fallback) rather than erroring — the UI explains this to the user.

## What's intentionally not built yet

- Scholarships module (same pattern as jobs — new router + service, reuse the
  aggregator design)
- Email integration (Gmail/Outlook draft-and-approve, not auto-send)
- Notifications, deadline reminders
- Docker/deployment config
- OAuth login (Google/Microsoft) — currently email/password only

These bolt on to the existing structure without a rewrite once the core loop
is solid.

## Adding LinkedIn later

LinkedIn has no public API for reading job listings — only a partner-gated
API for *posting* jobs (for ATS/employer integrations), which requires a
LinkedIn Business Development relationship. When you're ready to pursue that
path (or a licensed third-party data provider), add a new
`backend/app/services/linkedin_client.py` with a `search_jobs(params)`
function matching the same shape as `adzuna_client.py`, then register it in
`SOURCES` in `job_aggregator.py`. No other code changes needed.
