# MicCheck — Open Mic & Stand-Up Comedy Platform

A clone-style platform for open mic and lineup comedy shows: book performance spots, manage shows, and handle performer registration. Built with **Django** (backend API) and **Next.js** (frontend). The design is intentionally distinct to avoid copyright issues while offering the same flow as the reference site.

## Features

- **Home page**: Hero, stats, about, show formats, who can perform, how it works, testimonials
- **Booking page**: Select spots by date/time, apply coupon codes, enter performer details, submit booking
- **Django API**: Shows, spots, coupons, bookings with validation

## Project structure

```
miccheck/
├── backend/          # Django API
│   ├── miccheck/     # Project settings
│   └── bookings/     # App: Show, Spot, Coupon, Booking
├── frontend/         # Next.js app
│   └── src/
│       ├── app/      # Pages and layout
│       └── lib/      # API client
└── README.md
```

## Backend (Django)

Uses **PostgreSQL** in production with env-based config. Locally you can use SQLite (default) or PostgreSQL.

### Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Environment (production / PostgreSQL)

Copy `backend/.env.example` to `backend/.env` and set:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Long random secret (required in production) |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated domains, e.g. `api.yourdomain.com` |
| `DATABASE_URL` | PostgreSQL URL, e.g. `postgresql://user:pass@host:5432/dbname` |
| or `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Alternative to `DATABASE_URL` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend URLs (e.g. your Vercel app) |

If no `DATABASE_URL` or PostgreSQL env vars are set, Django falls back to SQLite for local dev.

### Database and admin

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for admin
python manage.py seed_spots        # sample shows, spots, coupon iLoveVC2
```

### Run locally

```bash
python manage.py runserver
```

API base: **http://localhost:8000/api/**

- `GET /api/spots/` — list spots
- `GET /api/shows/` — list shows with spots
- `POST /api/coupon/validate/` — body: `{ "code": "...", "spot_count": 6 }`
- `POST /api/bookings/` — body: `{ "spot_ids": [...], "performer_name", "email", "phone", "coupon_code?" }`

Admin: **http://localhost:8000/admin/**

## Frontend (Next.js)

### Setup

```bash
cd frontend
npm install
```

### Environment

Create `frontend/.env.local` (optional):

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

If not set, the app uses `http://localhost:8000/api` by default.

### Run

```bash
npm run dev
```

Open **http://localhost:3000**

- **/** — Home
- **/book** — Spot registration / booking

## Deployment (Vercel + backend)

- **Frontend (Next.js)** → deploy to **Vercel**. In Vercel project settings, set:
  - `NEXT_PUBLIC_API_URL` = your Django API base URL (e.g. `https://your-django-app.railway.app/api`).
- **Backend (Django)** → deploy to a platform that supports Python + PostgreSQL (e.g. **Railway**, **Render**, **Fly.io**). Django is not run on Vercel (Vercel is for the Next.js app).

### Backend deployment (Railway / Render example)

1. Create a new project and add a **PostgreSQL** service.
2. Add a **Web Service** (or “Django”): connect repo, root directory `backend`, build command `pip install -r requirements.txt`, start command `gunicorn miccheck.wsgi --bind 0.0.0.0:$PORT`.
3. Set environment variables from `backend/.env.example` (e.g. `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=your-backend-host`, `DATABASE_URL` from the PostgreSQL service, `CORS_ALLOWED_ORIGINS=https://your-app.vercel.app`).
4. Run migrations (one-off): `python manage.py migrate` (via shell or deploy hook).
5. Optionally run `python manage.py seed_spots` and create a superuser for admin.

After deploy, use the backend URL in `NEXT_PUBLIC_API_URL` for the Vercel frontend.

## Design notes

- **Brand**: “MicCheck” instead of the reference name; same idea (comedy stage, open mic, lineup).
- **Look**: Dark theme, amber/gold accent (#f59e0b), Outfit + DM Sans, card-based layout.
- **Content**: Same structure (hero, formats, how it works, testimonials, booking) with reworded copy to keep functionality without copying text.

## License

Use and modify as needed for your project.
