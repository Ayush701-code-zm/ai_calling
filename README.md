# AI Voice Caller

Monorepo: **FastAPI backend** + **Next.js frontend** for auth and outbound voice calls (Exotel + Pipecat + Gemini).

## Project structure

```
lite/
├── backend/src/     # Your original API (moved here)
└── frontend/        # Next.js app (login, register, dashboard)
```

There is **no** `src/` folder at the repo root — backend code lives only under `backend/src/`.

## Backend flow

```
main.py → uvicorn → app.py
  ├── startup: MongoDB (connect_to_mongo)
  ├── /api/v1/auth/*     → register, login, me (JWT)
  ├── /api/v1/calls/*    → outbound call, Exotel webhook
  ├── /ws/voice          → Pipecat + Gemini (Exotel stream)
  └── /health
```

### Run backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-core.txt
cp .env.example .env   # add your MongoDB URI and JWT_SECRET_KEY
python -m src.main
```

API: `http://localhost:8000`

## Frontend (Next.js)

### Run frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

App: `http://localhost:3000`

| Route | Purpose |
|-------|---------|
| `/login` | Sign in |
| `/register` | Create account |
| `/dashboard` | User info + place outbound call |

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

Ensure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`.

## Auth API

- `POST /api/v1/auth/register` — `{ email, password, full_name }`
- `POST /api/v1/auth/login` — `{ email, password }`
- `GET /api/v1/auth/me` — Bearer token

## Calls API

- `POST /api/v1/calls/outbound` — `{ phone_number, customer_name }`
- `POST /api/v1/calls/webhooks/exotel` — Exotel callback
- `WS /ws/voice` — real-time audio
