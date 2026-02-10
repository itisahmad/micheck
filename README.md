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

### Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Database and admin

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for admin
python manage.py seed_spots        # sample shows, spots, coupon iLoveVC2
```

### Run

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

## Design notes

- **Brand**: “MicCheck” instead of the reference name; same idea (comedy stage, open mic, lineup).
- **Look**: Dark theme, amber/gold accent (#f59e0b), Outfit + DM Sans, card-based layout.
- **Content**: Same structure (hero, formats, how it works, testimonials, booking) with reworded copy to keep functionality without copying text.

## License

Use and modify as needed for your project.
