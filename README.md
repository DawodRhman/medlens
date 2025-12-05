# MedLens — Cardiac Signal ML Platform

This repository is a starter full-stack project that demonstrates an end-to-end system for cardiac signal processing, model training, inference, and deployment.

Contents:
- `backend/` — FastAPI backend, ML models, preprocessing and training scripts.
- `frontend/` — React UI scaffold (login, dashboard, upload, waveform viewer).
- `docker-compose.yml` — Local development composition with backend, frontend, Postgres, and MongoDB.
- `k8s/` — Kubernetes manifests for deployment.
- `.github/workflows/ci.yml` — CI pipeline example.

Quick local dev (using PowerShell):

```powershell
cd C:/Users/USER/Desktop/medlens
docker-compose up --build

# Backend will be available at http://localhost:8000
# Frontend at http://localhost:5173
```

For iterative development without Docker:

```powershell
# Backend
cd backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

See `backend/README.md` and `frontend/README.md` for more details.
