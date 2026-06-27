# 🏨 Hotel Intelligence Project Roadmap

## Phase 1: Environment & Big Data 
- [x] Initialize Git & Virtual Env.
- [x] Create 'Data Loader' script (`data_loader.py`) for the Kaggle 515k dataset.
- [x] Setup Docker orchestration (PostgreSQL, API, Dashboard).
- [ ] Download Kaggle 515k Hotel Reviews dataset (User required).

## Phase 2: The AI Engine (ABSA) 
- [x] Integrate Hugging Face `transformers` library (`ml_engine.py`).
- [x] Implement Aspect-Extraction logic (**Targeting: Staff, Cleanliness, Food, Location, Value, WiFi**).
- [x] Create a local inference test script (`test_model.py`).

## Phase 3: The Backend
- [x] Build FastAPI skeleton with Pydantic schemas.
- [x] Implement background bulk processing with FastAPI BackgroundTasks.
- [x] Create job status endpoint with real progress tracking.
- [x] Add Alembic migrations and `/api/v1` route structure.
- [x] Improve ABSA pipeline with NLTK sentence splitting.
- [x] Add pytest coverage for ML engine and API endpoints.

## Phase 3: Auth & Data Ingestion
- [x] JWT authentication (register/login).
- [x] User-scoped reviews and jobs.
- [x] CSV multipart upload endpoint.
- [x] Streamlit dashboard login flow.

## Phase 4: React Frontend
- [x] Scaffold Vite + React + TypeScript + Tailwind.
- [x] Auth pages with JWT token storage.
- [x] Dashboard with KPI cards and Recharts aspect chart.
- [x] CSV upload UI with progress tracking.
- [x] Live analyze panel and review feed.
- [x] Dark/light mode and TanStack Query data fetching.

## Phase 5: Persistence & UI (Legacy)
- [x] Connect PostgreSQL to store final sentiment scores.
- [x] Build Streamlit premium dashboard with **Vibe Heatmap** and **Actionable Insights**.
- [x] Create **Intelligence Seeder** (`seed_data.py`) for instant data visualization.

## Phase 5: Analytics & Delivery
- [x] Paginated review search and filtering.
- [x] Sentiment trends over time (weekly/monthly).
- [x] AI executive insights and recommendations.
- [x] Downloadable PDF reports.
- [x] GitHub Actions CI for backend and frontend.

## Phase 6: MLOps & Delivery (Legacy)
- [x] Finalize `docker-compose.yml` for one-click deployment.
- [x] Write a README with architecture diagrams.
- [ ] Deploy live demo on Render/AWS.
