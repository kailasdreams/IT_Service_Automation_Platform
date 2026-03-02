# IT Service Automation Platform (AMFI)

Full-stack implementation for ITIL Process Automation, NMS Integration & Automated Troubleshooting.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+), SQLAlchemy, SQLite
- **Frontend:** React 18, TypeScript, Vite
- **Auth:** JWT (optional)

## Quick Start

### 1. Backend

```bash
cd c:\Users\OM-SAI\Desktop\AMFI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

API runs at http://localhost:8000. Docs: http://localhost:8000/docs

### 2. Seed Data (optional)

```bash
python scripts/seed.py
```

Creates admin user (admin/admin123) and sample integrations.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000 with API proxy to backend.

## Modules

| Module | Backend API | Frontend Page |
|--------|-------------|---------------|
| Dashboard | `/api/metrics/dashboard` | `/` |
| Incidents | `/api/incidents` | `/incidents` |
| Events | `/api/events` | `/events` |
| Integrations | `/api/integrations` | `/integrations` |
| Metrics | `/api/metrics/targets` | `/metrics` |
| Architecture | - | `/architecture` |
| Auth | `/api/auth` | (API only) |

## Project Structure

```
AMFI/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── config.py
│   ├── database.py
│   ├── models/          # SQLAlchemy models
│   └── routers/         # API routes
├── frontend/
│   ├── src/
│   │   ├── pages/       # React pages
│   │   ├── components/
│   │   └── api/
│   └── package.json
├── scripts/
│   └── seed.py
├── requirements.txt
└── run.py
```
