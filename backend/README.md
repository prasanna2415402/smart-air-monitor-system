# Smart Air Monitor System — Backend API

A production-ready **Django + Django REST Framework** backend for the Smart
Air Monitor System, built to connect directly to the provided frontend
(Next.js signup/login/dashboard pages) without changing any UI. It also
absorbs the data model and alerting logic of the original Streamlit/ESP32
prototype (`smart_iaq_system.zip`) — stations, sensors, readings, AQI
scoring, and threshold alerts — behind a clean REST API.

---

## 1. Features

- **JWT authentication** (access + refresh, rotation, blacklist-on-logout) via `djangorestframework-simplejwt`
- **Role-Based Access Control**: `ADMIN`, `OPERATOR`, `VIEWER`, enforced with reusable DRF permission classes
- **Secure signup → pending-approval → login** flow matching the frontend's signup form 1:1
- **CRUD APIs** for Users, Stations, Sensors, Sensor Readings, Alerts, Dashboard, Settings, and Backup/Restore
- **Input validation, uniform error/response envelopes, pagination, filtering & search** on every list endpoint
- **Swagger / ReDoc API docs** auto-generated at `/api/docs/` and `/api/redoc/`
- **Database backup & restore** (JSON fixtures) from the Admin-only Settings page
- **`.env`-driven config**, CORS enabled, SQLite for local dev / PostgreSQL for production
- **Clean layered architecture**: one Django app per bounded context, each with its own `models / serializers / views / urls / admin`
- **Seed command** that creates a superuser, sample users (incl. pending approvals), 3 stations, 18 sensors, and ~450 historical readings with realistic AQI/alert data

---

## 2. Folder Structure

```
smart_air_monitor_backend/
├── manage.py
├── requirements.txt
├── .env.example                # copy to .env
├── .gitignore
├── config/                     # project-level settings
│   ├── settings.py
│   ├── urls.py                 # root URL conf + Swagger/ReDoc
│   ├── wsgi.py / asgi.py
├── apps/
│   ├── core/                   # shared building blocks (no models)
│   │   ├── pagination.py       # StandardResultsSetPagination (envelope w/ count/pages)
│   │   ├── permissions.py      # IsAdmin, IsOperatorOrAdmin, IsViewerOrAbove, IsSelfOrAdmin
│   │   ├── exceptions.py       # custom_exception_handler -> uniform error JSON
│   │   ├── responses.py        # success_response()/error_response() helpers
│   │   ├── middleware.py       # request/response logging
│   │   └── management/commands/seed_data.py
│   ├── accounts/                # Users, Auth, RBAC, Profile
│   │   ├── models.py            # custom User model (AbstractBaseUser)
│   │   ├── managers.py          # UserManager (create_user/create_superuser)
│   │   ├── validators.py        # ComplexPasswordValidator (matches frontend zod rules)
│   │   ├── serializers.py       # Register/Login/User/Profile/ChangePassword
│   │   ├── views.py             # Register, Login, Logout, Refresh, Profile, UserViewSet (approve/reject/suspend)
│   │   └── urls.py
│   ├── stations/                 # Monitoring stations / zones
│   ├── sensors/                  # Sensors, SensorReadings, AlertLog, ingest endpoint, AQI engine (alerts.py)
│   ├── dashboard/                 # Aggregated /api/dashboard/summary/ endpoint (no models)
│   ├── settings_app/              # Singleton SystemSettings (thresholds, refresh interval, theme)
│   └── backup/                    # BackupRecord / RestoreRecord + create/list/download/restore
├── media/                          # uploaded profile photos + generated backups (gitignored)
├── logs/                           # rotating app.log (gitignored)
└── staticfiles/                    # collectstatic output (gitignored)
```

---

## 3. Quick Start (SQLite, local dev)

```bash
cd smart_air_monitor_backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # defaults already use SQLite (USE_SQLITE=True)

python manage.py migrate
python manage.py seed_data        # creates admin + sample users/stations/sensors/readings
python manage.py runserver
```

The API is now live at **http://127.0.0.1:8000/api/** and interactive docs
at **http://127.0.0.1:8000/api/docs/**.

**Seeded login (Admin):**
```
identifier: admin@smartair.com   (or username: admin)
password:   Admin@12345
```
**Seeded Operator/Viewer accounts** (already approved): `james.operator` /
`sara.viewer`, password `Passw0rd!`. Three other sample users are seeded
`PENDING` so you can immediately test the approve/reject workflow.

> ⚠️ Change `DJANGO_SUPERUSER_PASSWORD` and `SECRET_KEY` before deploying anywhere real.

### Switching to PostgreSQL

In `.env`:
```
USE_SQLITE=False
DB_NAME=smart_air_monitor
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```
Then create the database (`createdb smart_air_monitor`) and re-run
`python manage.py migrate && python manage.py seed_data`.

---

## 4. Connecting the Provided Frontend

The Next.js frontend's signup form and register API route (`src/app/api/auth/register/route.ts`)
map field-for-field onto `POST /api/auth/register/` below — no UI changes
needed, just point the frontend's fetch calls at this backend's base URL
(set `CORS_ALLOWED_ORIGINS` in `.env` to your frontend's dev URL, e.g.
`http://localhost:3000`).

| Frontend page/action | Backend endpoint |
|---|---|
| Signup form submit | `POST /api/auth/register/` |
| Login form submit | `POST /api/auth/login/` (send `{identifier, password}`, `identifier` = email or username) |
| Dashboard load | `GET /api/dashboard/summary/` |
| Logout | `POST /api/auth/logout/` (send `{refresh}`) |
| Profile page | `GET/PATCH /api/profile/me/` |

All authenticated requests need `Authorization: Bearer <access_token>`.

---

## 5. API Reference (v1, base path `/api/`)

### Auth
| Method | Endpoint | Access | Notes |
|---|---|---|---|
| POST | `/auth/register/` | Public | Creates account with `PENDING` status |
| POST | `/auth/login/` | Public | `{identifier, password}` → tokens + user; blocked while `PENDING`/`REJECTED`/`SUSPENDED` |
| POST | `/auth/logout/` | Authenticated | Blacklists the given refresh token |
| POST | `/auth/token/refresh/` | Public | Rotates refresh token |

### Users (Admin only, except self-profile)
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/users/` | List, filter by `role`, `account_status`, `is_active`; search `full_name/username/email/employee_id` |
| GET | `/users/pending/` | Pending-registrations widget |
| POST | `/users/{id}/approve/` | Approve + activate |
| POST | `/users/{id}/reject/` | `{reason}` |
| POST | `/users/{id}/suspend/` | Suspend an active account |
| PATCH/PUT/DELETE | `/users/{id}/` | Manage role/status/active flag |

### Profile (any authenticated user, self only)
| Method | Endpoint |
|---|---|
| GET / PATCH | `/profile/me/` |
| POST | `/profile/change-password/` |

### Stations (read: any approved user · write: Operator/Admin)
`GET/POST /stations/`, `GET/PUT/PATCH/DELETE /stations/{id}/` — filter by `status`, search `name/code/location`.

### Sensors & Readings
| Method | Endpoint | Notes |
|---|---|---|
| GET/POST/PUT/PATCH/DELETE | `/sensors/` | filter `station`, `sensor_type`, `status` |
| POST | `/sensors/ingest/` | Operator/Admin — push a reading (ESP32/simulator payload); auto-computes AQI, alert level, fan state, and raises `AlertLog` rows |
| GET | `/sensors/readings/` | filter `station`, `sensor`, `alert_level`, `start`, `end`, `min_aqi`, `max_aqi`, `recent_minutes` |
| GET | `/sensors/readings/latest/?station=&n=` | Live metric cards |
| GET | `/sensors/readings/worst_events/?limit=` | Highest-AQI events |
| GET | `/sensors/readings/report/?period=daily|weekly|monthly&station=` | Hourly/daily aggregate buckets |
| DELETE | `/sensors/readings/delete_range/?start=&end=` | Operator/Admin |
| GET | `/sensors/alerts/` | filter `station`, `severity`, `is_acknowledged` |
| POST | `/sensors/alerts/{id}/acknowledge/` | Operator/Admin |

### Dashboard
`GET /dashboard/summary/` — stats cards, live per-station readings, current AQI, pending registrations, in one call.

### Settings (read: any approved user · write: Admin)
`GET/PUT/PATCH /settings/`, `POST /settings/reset/` — theme, auto-refresh, and every CO2/temp/humidity/PM2.5/PM10/AQI threshold.

### Backup / Restore (Admin only)
| Method | Endpoint |
|---|---|
| GET | `/backup/` — list backups |
| POST | `/backup/create_backup/` — dump `accounts, stations, sensors, settings_app` to a JSON fixture |
| GET | `/backup/{id}/download/` — download the fixture file |
| DELETE | `/backup/{id}/` — remove backup record + file |
| POST | `/backup/restore/` — multipart upload `{file, confirm=true}`, restores via `loaddata` |
| GET | `/backup/restore-history/` — audit trail |

Every list endpoint returns:
```json
{ "success": true, "count": 42, "total_pages": 3, "current_page": 1, "page_size": 20, "next": "...", "previous": null, "results": [...] }
```
Every error returns:
```json
{ "success": false, "message": "Human readable summary.", "errors": { "field": ["..."] } }
```

---

## 6. Django Admin

`http://127.0.0.1:8000/admin/` — log in with the seeded superuser to manage
every model directly (useful for support/ops), including read-only audit
tables (`RefreshTokenAudit`, `RestoreRecord`).

---

## 7. Testing What You've Got

```bash
python manage.py check                 # config/system checks
python manage.py test                  # basic smoke tests (apps/*/tests.py)
```

A quick manual smoke test with `curl`:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin@smartair.com","password":"Admin@12345"}'
```

---

## 8. Production Notes

- Set `DEBUG=False`, a strong random `SECRET_KEY`, and real `ALLOWED_HOSTS` in `.env`.
- Switch `USE_SQLITE=False` and point at a real PostgreSQL instance.
- Run behind Gunicorn + a reverse proxy (Nginx): `gunicorn config.wsgi:application`.
- `whitenoise` is already wired up for static file serving; run `python manage.py collectstatic`.
- Rotate `SECRET_KEY` and re-issue tokens if it's ever leaked — SimpleJWT tokens are signed with it.
- The auth endpoints are throttled (`10/min`) and the ingest endpoint (`120/min`) via DRF's `ScopedRateThrottle` — tune `DEFAULT_THROTTLE_RATES` in `config/settings.py` for your load.
- Back up the Postgres database itself (e.g. `pg_dump`) in addition to the in-app JSON backups, which only cover application tables (not sessions/auth-framework internals).

---

## 9. Where the Original Prototype's Logic Went

The uploaded `smart_iaq_system.zip` (Streamlit + ESP32 prototype) contributed:
- Its `air_quality_readings` schema → `apps.sensors.models.SensorReading`
- Its `alerts.py` threshold/AQI logic → ported verbatim into `apps.sensors.alerts` and wired into the `/sensors/ingest/` endpoint
- Its Settings page fields (COM port, baud rate, thresholds) → `apps.settings_app.models.SystemSettings`

The uploaded `smart-air-monitor-signup.zip` (Next.js frontend) contributed:
- Its `src/db/schema.ts` user fields → `apps.accounts.models.User`
- Its signup form's password/terms validation → `apps.accounts.validators.ComplexPasswordValidator` and `RegisterSerializer`
