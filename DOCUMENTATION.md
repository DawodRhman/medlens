# MedLens — Cardiac Signal ML Platform - Full Documentation

A comprehensive full-stack system for ECG/PCG signal classification, anomaly detection, and clinical decision support. Demonstrates end-to-end ML pipeline, backend APIs, secure authentication, containerization, and cloud deployment.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [Backend API Documentation](#backend-api-documentation)
- [Machine Learning Models](#machine-learning-models)
- [Database & Storage](#database--storage)
- [Authentication & Security](#authentication--security)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Docker Compose (Recommended)

```powershell
cd C:\Users\USER\Desktop\medlens
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Default credentials: `admin` / `admin`

### Manual Setup (Development)

**Backend:**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install alembic
alembic upgrade head
python app/db/seed_admin.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (in separate terminal):**
```powershell
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
medlens/
├── backend/
│   ├── app/
│   │   ├── api/                    # API routers
│   │   │   ├── auth.py             # JWT login/register
│   │   │   ├── predict.py          # Signal classification
│   │   │   ├── anomaly.py          # Anomaly detection
│   │   │   ├── upload.py           # Signal upload & storage
│   │   │   └── analytics.py        # Model metrics & dashboards
│   │   ├── models/
│   │   │   ├── trainable_models.py # PyTorch CNN & Autoencoder
│   │   │   ├── pytorch_models.py   # Model stubs & loaders
│   │   │   └── MODEL_CARDS.md      # Model documentation
│   │   ├── services/
│   │   │   ├── predict_service.py  # Inference wrapper
│   │   │   ├── anomaly_service.py  # Anomaly scoring
│   │   │   └── analytics_service.py# Metrics aggregation
│   │   ├── utils/
│   │   │   ├── preprocess.py       # Signal preprocessing
│   │   │   ├── jwt.py              # JWT token handling
│   │   │   ├── deps.py             # FastAPI dependencies
│   │   │   └── metrics.py          # Prometheus metrics
│   │   ├── db/
│   │   │   ├── sql_models.py       # SQLAlchemy ORM models
│   │   │   ├── storage.py          # MongoDB blob storage
│   │   │   └── seed_admin.py       # Admin user seeding
│   │   ├── middleware/
│   │   │   └── rate_limit.py       # Rate limiting
│   │   ├── train/
│   │   │   └── train.py            # Model training & export
│   │   └── main.py                 # FastAPI app entry
│   ├── alembic/                    # Database migrations
│   ├── alembic.ini                 # Migration config
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend container
│   └── README.md                   # Backend-specific docs
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx           # JWT login
│   │   │   ├── Dashboard.jsx       # Main dashboard
│   │   │   └── Upload.jsx          # Signal upload
│   │   ├── App.jsx                 # Root component
│   │   ├── main.jsx                # Entry point
│   │   └── styles.css              # Global styles
│   ├── package.json                # Node dependencies
│   ├── index.html                  # HTML template
│   ├── Dockerfile                  # Frontend container
│   └── README.md                   # Frontend-specific docs
├── k8s/
│   ├── backend-deployment.yaml     # Kubernetes backend
│   └── frontend-deployment.yaml    # Kubernetes frontend
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline
├── docker-compose.yml              # Local dev orchestration
├── .gitignore                      # Git ignore rules (secrets, models)
└── README.md                       # Main README
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              http://localhost:5173                          │
│  ┌─────────────────────────────────────────────────┐        │
│  │ Login → JWT Token → Dashboard → Upload Signal  │        │
│  │ Charts & Real-time Waveform Renderer           │        │
│  └─────────────────────────────────────────────────┘        │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS/WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                            │
│              http://localhost:8000                          │
│  ┌─────────────────────────────────────────────────┐        │
│  │ POST /auth/login       → JWT Token              │        │
│  │ POST /predict          → Signal Classification  │        │
│  │ POST /anomaly-detect   → Anomaly Score         │        │
│  │ POST /upload           → Store Raw Signal      │        │
│  │ GET  /analytics        → Model Metrics         │        │
│  │ GET  /metrics          → Prometheus Metrics    │        │
│  └─────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────┐        │
│  │ Services Layer                                  │        │
│  │ - PredictService (TorchScript/ONNX inference) │        │
│  │ - AnomalyService (Autoencoder)                │        │
│  │ - AnalyticsService (Metrics aggregation)      │        │
│  └─────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────┐        │
│  │ ML Models (PyTorch)                             │        │
│  │ - Conv1D Classifier (3 classes)                │        │
│  │ - SimpleAutoencoder (latent_dim=64)            │        │
│  │ - Signal Preprocessing Pipeline                │        │
│  └─────────────────────────────────────────────────┘        │
└────────────────┬────────────────┬──────────────────────────┘
                 │                │
        ┌────────▼────┐   ┌───────▼──────┐
        │  PostgreSQL │   │   MongoDB    │
        │  (Patients, │   │ (Raw Signals,│
        │  Records,   │   │  Predictions)│
        │  Predictions)   │              │
        └─────────────┘   └──────────────┘
```

---

## Setup & Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (for containerized dev)
- **PostgreSQL 15** (or via Docker)
- **MongoDB 6** (or via Docker)

### Environment Variables

Create a `.env` file in the `backend/` folder:

```bash
# Database
DATABASE_URL=postgresql://medlens:medlens@localhost:5432/medlens
MONGO_URL=mongodb://localhost:27017
MONGO_DB=medlens

# JWT & Security
JWT_SECRET=your-secret-key-here

# Sentry (optional monitoring)
SENTRY_DSN=

# AWS (optional cloud deployment)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### Backend Installation

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install alembic
```

### Database Setup

```powershell
# Run migrations
alembic upgrade head

# Seed admin user
python app/db/seed_admin.py
```

### Frontend Installation

```powershell
cd frontend
npm install
```

---

## Backend API Documentation

All endpoints require JWT authentication (except `/auth/login` and `/auth/register`).

### Authentication Endpoints

#### Register User
```
POST /auth/register

Request:
{
  "username": "technician1",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Login
```
POST /auth/login

Request:
{
  "username": "admin",
  "password": "admin"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```
GET /auth/me

Headers:
Authorization: Bearer <token>

Response:
{
  "username": "admin",
  "role": "admin"
}
```

### Signal Processing Endpoints

#### Classify Signal
```
POST /predict/

Headers:
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
file: <audio.wav>

Response:
{
  "label": "normal",
  "confidence": 0.92
}
```

#### Detect Anomaly
```
POST /anomaly/

Headers:
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
file: <audio.wav>

Response:
{
  "score": 0.15,
  "is_anomaly": false
}
```

#### Upload Signal
```
POST /upload/

Headers:
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
file: <audio.wav>
patient_id: <optional>

Response:
{
  "id": "uuid",
  "message": "uploaded"
}
```

### Analytics & Monitoring

#### Get Analytics (Doctor/Admin only)
```
GET /analytics/

Headers:
Authorization: Bearer <token>

Response:
{
  "metrics": {
    "model_accuracy": 0.92,
    "avg_latency_ms": 45,
    "drift_score": 0.02
  }
}
```

#### Prometheus Metrics
```
GET /metrics

Response: Prometheus-format metrics
```

#### Health Check
```
GET /health

Response:
{"status": "ok"}
```

### API Documentation

Full interactive Swagger docs available at:
```
http://localhost:8000/docs
```

---

## Machine Learning Models

### Training Models

Train and export models to TorchScript and ONNX:

```powershell
cd backend
python -m app.train.train
```

This will create:
- `models/classifier.pt` — PyTorch state dict
- `models/classifier_script.pt` — TorchScript (production-ready)
- `models/classifier.onnx` — ONNX format
- `models/autoencoder.pt` — Autoencoder state dict
- `models/autoencoder_script.pt` — TorchScript autoencoder
- `models/autoencoder.onnx` — ONNX autoencoder

**Note:** Model artifacts are in `.gitignore` and won't be committed to the repository.

### Model Architecture

#### Signal Classifier
- **Input:** 1D signal array (length: 10,000 samples)
- **Architecture:** 3-layer Conv1D + BatchNorm + Global Average Pooling
- **Output:** 3 classes (normal, murmur, arrhythmia) with probabilities
- **Inference time:** ~45ms

#### Anomaly Autoencoder
- **Input:** 1D signal array
- **Architecture:** Conv1D encoder → latent (dim=64) → Conv1D decoder
- **Output:** Reconstruction error score + boolean is_anomaly
- **Threshold:** score > 0.1 → anomaly

### Signal Preprocessing

All signals are preprocessed via `app/utils/preprocess.py`:
1. **Load audio** — Read WAV/FLAC/MP3 from bytes
2. **Bandpass filter** — 20-800 Hz butterworth filter (order=4)
3. **Normalize** — Scale to [-1, 1] range
4. **Segment** — Pad/truncate to 5-second window (10,000 samples @ 2kHz)

---

## Database & Storage

### PostgreSQL Schema

**Patients:**
```sql
CREATE TABLE patients (
  id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,
  dob DATETIME,
  metadata JSON
);
```

**Records:**
```sql
CREATE TABLE records (
  id INTEGER PRIMARY KEY,
  patient_id INTEGER FOREIGN KEY,
  created_at DATETIME DEFAULT NOW(),
  source VARCHAR,
  metadata JSON
);
```

**Predictions:**
```sql
CREATE TABLE predictions (
  id INTEGER PRIMARY KEY,
  record_id INTEGER FOREIGN KEY,
  label VARCHAR,
  confidence FLOAT,
  created_at DATETIME DEFAULT NOW(),
  extras JSON
);
```

**Users:**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  role VARCHAR DEFAULT 'technician',
  created_at DATETIME DEFAULT NOW()
);
```

### MongoDB Collections

**signals** — Raw audio blobs and metadata
```json
{
  "_id": "uuid",
  "created_at": "2025-11-29T10:00:00Z",
  "metadata": {
    "patient_id": "123",
    "signal_type": "ECG"
  },
  "blob": <binary>
}
```

### Database Migrations

Run migrations:
```powershell
alembic upgrade head
```

Create new migration after schema changes:
```powershell
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
```

---

## Authentication & Security

### JWT Tokens

- **Expiration:** 60 minutes (configurable)
- **Payload:** `{sub: username, role: role, exp: expiration}`
- **Algorithm:** HS256
- **Secret:** `JWT_SECRET` environment variable

### Roles

- **admin** — Full access (predictions, analytics, user management)
- **doctor** — Access to analytics and predictions
- **technician** — Access to predictions only

### Rate Limiting

In-memory limiter (60 requests per 60 seconds per IP):
```python
# Configured in app/middleware/rate_limit.py
# For production, use Redis-backed limiter
```

### Security Best Practices

1. **Never commit secrets** — Use `.env` file and `.gitignore`
2. **Hash passwords** — bcrypt with salt rounds=12
3. **Validate inputs** — Pydantic models on all endpoints
4. **CORS policy** — Restricted to `http://localhost:3000` (update for production)
5. **HTTPS only** — Enable in production Nginx/load balancer

---

## Deployment

### Docker Compose (Local Development)

```powershell
docker-compose up --build
```

### Kubernetes (Production)

```powershell
# Apply manifests
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Scale backend
kubectl scale deployment medlens-backend --replicas=3
```

### AWS Deployment (ECS/EKS)

1. Build and push images to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker tag medlens-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-backend:latest
   ```

2. Create RDS PostgreSQL instance:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier medlens-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username medlens \
     --master-user-password <password>
   ```

3. Create S3 bucket for raw signals:
   ```bash
   aws s3 mb s3://medlens-signals-prod
   ```

---

## Monitoring & Observability

### Prometheus Metrics

Endpoint: `GET /metrics`

Tracked metrics:
- `medlens_predictions_total` — Total predictions made
- `medlens_prediction_latency_seconds` — Latency histogram

### Grafana Dashboard

Example dashboard JSON (import into Grafana):
```json
{
  "dashboard": {
    "title": "MedLens Metrics",
    "panels": [
      {
        "title": "Predictions per minute",
        "targets": [{"expr": "rate(medlens_predictions_total[1m])"}]
      }
    ]
  }
}
```

### Logging

Logs output to stdout (compatible with ELK stack and CloudWatch):
- Backend logs via Uvicorn
- Application errors via FastAPI middleware

### Error Tracking (Sentry)

Configure in `.env`:
```bash
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

---

## Development Workflow

### Running Tests

```powershell
cd backend
pytest tests/ -v
```

### Code Formatting

```powershell
black app/
flake8 app/
```

### Hot Reload

Backend auto-reloads on file changes:
```powershell
uvicorn app.main:app --reload
```

Frontend hot-reload with Vite:
```powershell
npm run dev
```

### Git Workflow

```bash
git add .
git commit -m "feat: add new endpoint"
git push origin main
# CI/CD pipeline auto-runs on push
```

---

## Troubleshooting

### Backend fails to start

**Issue:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```powershell
cd backend
pip install -e .
```

### Database connection error

**Issue:** `could not connect to server`

**Solution:** Ensure PostgreSQL is running:
```powershell
docker-compose up -d postgres mongo
```

### Frontend can't reach backend

**Issue:** CORS error or connection refused

**Solution:** Verify backend is running on `http://localhost:8000`
```powershell
curl http://localhost:8000/health
```

### Model not found

**Issue:** Predictions fail with "model not found"

**Solution:** Train models:
```powershell
cd backend
python -m app.train.train
```

### JWT token invalid

**Issue:** `401 Unauthorized` on protected endpoints

**Solution:**
1. Re-login to get fresh token
2. Verify `Authorization: Bearer <token>` header format
3. Check JWT expiration (60 minutes)

---

## Next Steps & Enhancements

- [ ] Replace in-memory rate limiter with Redis
- [ ] Add WebSocket streaming for real-time inference
- [ ] Implement admin panel for reviewing predictions
- [ ] Add A/B testing framework for model versions
- [ ] Deploy to AWS EKS with auto-scaling
- [ ] Add comprehensive test suite with CI
- [ ] Integrate Sentry + Grafana dashboards
- [ ] Add email notifications for anomalies

---

## Support & Contribution

For issues, questions, or contributions, please open an issue or PR on GitHub.

---

## License

MIT License — See LICENSE file for details.
