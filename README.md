# Smart Air Monitor System

A unified, working full-stack project combining the three pieces you provided:

| Source .zip                        | Became                                                              |
|-------------------------------------|----------------------------------------------------------------------|
| `smart-air-monitor-signup.zip`      | `frontend/` — Next.js UI (signup, login, dashboard), rewired to call the Django API instead of its own Postgres/Drizzle database |
| `smart_air_monitor_backend.zip`     | `backend/` — Django REST API (already had accounts, stations, sensors, dashboard, settings, backup apps) |
| `smart_iaq_system.zip`              | Its rule engine (`alerts.py`) was already ported into `backend/apps/sensors/alerts.py`. Its AI/ML predictor (`ai_predictor.py`) is now ported into a new **`backend/apps/ai/`** Django app, wired into the API. The ESP32 firmware is kept for reference in `docs/esp32_firmware.ino`. |

Everything below has been built, migrated, type-checked, and smoke-tested in this environment.

---

## Architecture

```
                 JWT (Bearer) over HTTPS/HTTP
Next.js  ───────────────────────────────────▶  Django REST API  ───▶  SQLite / Postgres
(frontend/,                                    (backend/, port 8000)
 port 3000)                                          │
                                                       ├─ apps/accounts   (auth, RBAC, approval workflow)
                                                       ├─ apps/stations   (monitoring zones)
                                                       ├─ apps/sensors    (sensors, readings, ingest, alerts)
                                                       ├─ apps/dashboard  (aggregated summary endpoint)
                                                       ├─ apps/settings_app (threshold configuration)
                                                       ├─ apps/backup     (DB backup/restore)
                                                       └─ apps/ai         (NEW — AI/ML predictions, ported
                                                                            from smart_iaq_system/ai_predictor.py)
```

The frontend never talks to a database directly anymore — `frontend/src/lib/api.ts` is the single client
that calls the Django REST API at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) and stores the
JWT access/refresh tokens in cookies.

---

## What was fixed / connected

- **Frontend → Backend wiring**: the signup form posted straight to a local Postgres table via Drizzle
  ORM; the login page was fully mocked. Both now call the real Django endpoints
  (`POST /api/auth/register/`, `POST /api/auth/login/`) through `frontend/src/lib/api.ts`.
- **Dashboard**: was 100% static mock data. It now fetches `GET /api/dashboard/summary/` on load and
  every 15s, with a manual refresh button, sign-out, and redirect-to-login when unauthenticated.
- **Removed dead dependencies**: `drizzle-orm`, `drizzle-zod`, `drizzle-kit`, `pg`, `@types/pg`,
  `bcryptjs` (password hashing now happens once, in Django) and the `src/db/` folder are gone — the
  frontend is now a pure API client, no local database.
- **AI module integration**: `smart_iaq_system/ai_predictor.py` (RandomForest classifier + Gradient
  Boosting CO2 forecaster + IsolationForest anomaly detector, with a rule-based fallback until enough
  history exists) was ported into `backend/apps/ai/predictor.py`, reading from the `SensorReading` model
  via pandas instead of the prototype's standalone SQLite file. It's exposed as:
  - `GET /api/ai/predict/?station=<id>`
  - `GET /api/ai/status/?station=<id>`
  Models are trained lazily and cached in-process per station (see `get_predictor_for_station`), retraining
  automatically every ~20 new readings — this was smoke-tested end-to-end with 90 synthetic readings.
- **Import/dependency fixes**: `requirements.txt` had a nonexistent `Pillow==11.4.0` pin (fixed to
  `11.3.0`); added `numpy`, `pandas`, `scikit-learn` for the new AI app; `apps.ai` was registered in
  `INSTALLED_APPS` and `config/urls.py`.
- **Verified**: `python manage.py check`, `makemigrations`, and `migrate` all pass cleanly; a full
  register → login → dashboard-summary → ai-predict round trip was tested via Django's test client;
  the frontend passes `tsc --noEmit` and `next build` with zero errors.

---

## Field mapping (frontend ⇄ backend), so nothing gets lost in translation

The Django `RegisterSerializer` was written to mirror the signup form 1:1. `frontend/src/lib/api.ts`
does the camelCase → snake_case + role-uppercasing translation for you:

| Frontend form field | Backend field      |
|----------------------|--------------------|
| `fullName`           | `full_name`        |
| `mobileNumber`        | `mobile_number`    |
| `employeeId`          | `employee_id`      |
| `confirmPassword`     | `confirm_password` |
| `role` (`Operator`/`Viewer`) | `role` (`OPERATOR`/`VIEWER`) |
| `termsAccepted`       | `terms_accepted`   |

Note: self-registration as **Admin** is intentionally disallowed by the backend (`RegisterSerializer.validate_role`),
so the "Admin" option was removed from the signup form's role selector. Create the first admin with
`python manage.py createsuperuser` or the `seed_data` management command below.

---

## Running it locally

### 1. Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # defaults to SQLite, no Postgres needed

python manage.py migrate

# Optional but recommended: creates an approved admin user, sample
# stations/sensors, and ~200 historical readings per station (enough
# to immediately exercise the AI module's ML path, not just the
# rule-based fallback):
python manage.py seed_data

# Or just a bare superuser instead:
# python manage.py createsuperuser

python manage.py runserver 0.0.0.0:8000
```

The API is now at `http://localhost:8000/api/`, with interactive docs at
`http://localhost:8000/api/docs/` (Swagger) and `/api/redoc/`.

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:3000`. `backend/config/settings.py` already allows CORS from
`http://localhost:3000` by default (`CORS_ALLOWED_ORIGINS` in `.env`).

### 3. Try the AI endpoint directly

```bash
# Get a token first (use the seed_data admin, or your own approved user)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin@smartair.com","password":"Admin@12345"}' | python -c "import sys,json;print(json.load(sys.stdin)['data']['access'])")

curl -s "http://localhost:8000/api/ai/predict/?station=1" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

---

## Final folder structure

```
smart-air-monitor-system/
├── README.md                      ← this file
│
├── backend/                       ← Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   ├── settings.py            (apps.ai registered here)
│   │   ├── urls.py                (api/ai/ wired in here)
│   │   ├── asgi.py / wsgi.py
│   ├── apps/
│   │   ├── core/                  shared responses, permissions (RBAC), pagination, exception handler
│   │   ├── accounts/               custom User model, JWT auth, register/login/approve/reject
│   │   ├── stations/                monitoring zones
│   │   ├── sensors/                 sensors, readings, ingest endpoint, alerts.py (AQI/threshold engine)
│   │   ├── dashboard/                GET /api/dashboard/summary/
│   │   ├── settings_app/             system threshold configuration (singleton)
│   │   ├── backup/                   DB backup/restore
│   │   └── ai/                     ★ NEW — ported from smart_iaq_system/ai_predictor.py
│   │       ├── predictor.py         AIPredictor: RandomForest + GradientBoosting + IsolationForest
│   │       ├── views.py             GET /api/ai/predict/, GET /api/ai/status/
│   │       └── urls.py
│   ├── media/ , staticfiles/ , logs/
│
├── frontend/                      ← Next.js UI
│   ├── package.json                (drizzle/pg/bcryptjs removed)
│   ├── .env.local.example
│   ├── src/
│   │   ├── lib/
│   │   │   └── api.ts             ★ NEW — single API client (auth, tokens, dashboard, AI)
│   │   └── app/
│   │       ├── page.tsx            landing page
│   │       ├── signup/page.tsx     now calls registerUser() → Django
│   │       ├── login/page.tsx      now calls loginUser() → Django JWT
│   │       ├── dashboard/page.tsx  now fetches real /api/dashboard/summary/
│   │       └── api/health/route.ts proxies a health check to the Django backend
│
└── docs/
    └── esp32_firmware.ino          kept for reference from smart_iaq_system (hardware ingest client)
```
