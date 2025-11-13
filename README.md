# HealthLab

HealthLab is a full-stack nutrition intelligence platform that combines data-rich ingredient exploration, guided meal planning, and day-to-day wellness tracking. The application pairs a modular FastAPI backend with a responsive React experience that centers users around actionable insights—dynamic journals, ingredient enrichment, and tailored nutrition plans that stay aligned with their goals.

## Product Overview

- **Personalized daily dashboard** with calorie goals, macro progress, health-pillar insights, and an always-on journal.
- **Meal planning workflow** featuring dynamic recipe exploration, meal logging, and AI-assisted plan generation.
- **Ingredient intelligence** with curated compound, vitamin, and mineral research surfaced directly inside ingredient profiles.
- **Goal-driven onboarding** that captures lifestyle, preferences, and targeted outcomes to tune recommendations.
- **Operational tooling** for enriching ingredient data, running analysis scripts, and verifying the quality of curated datasets.

## Architecture at a Glance

- **Frontend (`frontend/`)**  
  React + Vite single-page app with Context-managed state, modular UI components, Framer Motion animations, and Lucide iconography. Modals and overlays use responsive, self-centering layouts that stay usable while the page scrolls.

- **Backend (`backend/`)**  
  FastAPI service with a service-layer architecture, SQLAlchemy models, bcrypt-secured authentication, and JWT-based session management. Ingredient enrichment pipelines stitch together compound/vitamin research, user data, and meal planning logic.

- **Data Enrichment (`backend/analysis/`)**  
  Scripts generate detailed compound and micronutrient descriptions, merge enrichment data into ingredient catalogs, and flag any remaining gaps prior to deployment.

## Tech Stack

- **Frontend:** React 18, Vite, Framer Motion, Context API, lucide-react
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Pydantic v2, bcrypt, PyJWT
- **Database:** SQLite (development) with JSON fields, ready to scale to PostgreSQL
- **Tooling:** ESLint, Jest-ready setup, Pytest, Requests, ResizeObserver-powered UI utilities

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- (Optional) SQLite CLI for inspecting the local database

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Environment variables are read from `.env` (see `.env.example`). Defaults target `sqlite:///./healthlab.db` and development CORS origins.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies API requests to `http://localhost:8000/api/v1` (configurable via `VITE_API_BASE_URL`).

### Run Both Services Together

1. Start the backend (`uvicorn app.main:app --reload --port 8000`)
2. Start the frontend (`npm run dev`)
3. Visit `http://localhost:5173` and log in using a seeded account or create a new one.

## Key Workflows & Scripts

- `backend/analysis/build_nutrient_descriptions.py` – generates detailed compound and micronutrient reference data.
- `backend/analysis/build_ingredient_enrichment.py` – fuses enrichment data into ingredient entities and produces `ingredient_enrichment.json`.
- `backend/scripts/init_db.py` – bootstraps the HealthLab database from curated JSON exports.
- `backend/tests/run_tests.py` – convenience runner for API, service, and model pytest suites.
- `frontend/src/context/DataContext.jsx` – centralizes meal plans, logged meals, ingredient details, and summaries for UI consumption.

## Running Tests

- **Backend:** `cd backend && pytest`
- **Frontend:** `cd frontend && npm run lint` (unit tests can be added via Jest/Vitest as needed)

## Project Structure

```
HealthLab/
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI routers (auth, meals, entities, analytics, etc.)
│   │   ├── models/            # SQLAlchemy models (Entity, User, Relationships, Health Pillars)
│   │   ├── schemas/           # Pydantic response/request models
│   │   ├── services/          # Business logic and data access helpers
│   │   └── main.py            # FastAPI entry point
│   ├── analysis/              # Data enrichment + reporting scripts
│   ├── scripts/               # Operational utilities and data ingestion scripts
│   ├── tests/                 # API, model, and service test suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # Dashboard, modals, onboarding, meal planning, etc.
│   │   ├── context/           # Auth and data providers
│   │   ├── pages/             # Ingredient detail, dashboard, authentication views
│   │   └── services/          # API clients and helper utilities
│   ├── public/                # Static assets
│   ├── package.json
│   └── vite.config.js
├── README.md                  # You are here
├── SETUP.md                   # Extended environment notes (updated for HealthLab)
├── UI-UX-GUIDELINES.md        # Design system and interaction principles
└── HEALTH_PILLAR_TEST_RESULTS.md
```

## Deployment Notes

- Build the frontend with `npm run build`; deploy `frontend/dist` to your static host of choice.
- Package the backend with your preferred ASGI server (e.g., `uvicorn` or `gunicorn`) and configure environment variables for production secrets, database URL, and CORS origins.
- Update `.env`/infrastructure secrets with the new application name (`HEALTHLAB`) and JWT signing key before production rollout.

## Contributing

1. Create a feature branch from `main`.
2. Make your changes with accompanying tests or lint passes.
3. Submit a PR with a description of the feature or fix.

---

HealthLab is licensed under the MIT License. Crafted with a focus on nutritional insight, data integrity, and a seamless product experience.
