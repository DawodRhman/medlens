# MedLens API Reference

Complete reference for all MedLens backend API endpoints with examples, request/response formats, and error codes.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

## Status Codes

- **200** — OK
- **201** — Created
- **400** — Bad Request
- **401** — Unauthorized
- **403** — Forbidden
- **404** — Not Found
- **429** — Too Many Requests (rate limited)
- **500** — Internal Server Error

---

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**No authentication required**

**Response:**
```json
{
  "status": "ok"
}
```

**cURL:**
```bash
curl http://localhost:8000/health
```

---

### Authentication

#### POST /auth/register

Create a new user account.

**No authentication required**

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (400):**
```json
{
  "detail": "User exists"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password_123"
  }'
```

---

#### POST /auth/login

Authenticate and get a JWT token.

**No authentication required**

**Request:**
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (401):**
```json
{
  "detail": "Invalid credentials"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

---

#### GET /auth/me

Get information about the current user.

**Requires authentication**

**Response (200):**
```json
{
  "username": "admin",
  "role": "admin"
}
```

**Error (401):**
```json
{
  "detail": "Invalid token"
}
```

**cURL:**
```bash
TOKEN="your_jwt_token_here"
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

### Signal Processing

#### POST /predict/

Classify a cardiac signal into categories: normal, murmur, or arrhythmia.

**Requires:** technician or doctor or admin role

**Request:**
- Content-Type: multipart/form-data
- Parameters:
  - `file` (required): WAV/MP3/FLAC audio file

**Response (200):**
```json
{
  "label": "normal",
  "confidence": 0.92
}
```

**Error (401):**
```json
{
  "detail": "Invalid token"
}
```

**Error (403):**
```json
{
  "detail": "Insufficient role"
}
```

**cURL:**
```bash
TOKEN="your_jwt_token_here"
curl -X POST http://localhost:8000/predict/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@signal.wav"
```

**Python:**
```python
import requests

token = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {token}"}

with open("signal.wav", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/predict/",
        headers=headers,
        files=files
    )
    print(response.json())
```

---

#### POST /anomaly/

Detect anomalous patterns in a cardiac signal.

**Requires:** technician or doctor or admin role

**Request:**
- Content-Type: multipart/form-data
- Parameters:
  - `file` (required): WAV/MP3/FLAC audio file

**Response (200):**
```json
{
  "score": 0.15,
  "is_anomaly": false
}
```

**cURL:**
```bash
TOKEN="your_jwt_token_here"
curl -X POST http://localhost:8000/anomaly/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@signal.wav"
```

---

### Storage

#### POST /upload/

Store a raw cardiac signal and metadata.

**Requires:** technician or doctor or admin role

**Request:**
- Content-Type: multipart/form-data
- Parameters:
  - `file` (required): WAV/MP3/FLAC audio file
  - `patient_id` (optional): Patient identifier

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "uploaded"
}
```

**cURL:**
```bash
TOKEN="your_jwt_token_here"
curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@signal.wav" \
  -F "patient_id=patient123"
```

---

### Analytics & Monitoring

#### GET /analytics/

Get model performance metrics and system analytics.

**Requires:** doctor or admin role

**Response (200):**
```json
{
  "metrics": {
    "model_accuracy": 0.92,
    "avg_latency_ms": 45,
    "drift_score": 0.02
  }
}
```

**Error (403):**
```json
{
  "detail": "Insufficient role"
}
```

**cURL:**
```bash
TOKEN="your_jwt_token_here"
curl http://localhost:8000/analytics/ \
  -H "Authorization: Bearer $TOKEN"
```

---

#### GET /metrics

Prometheus-format metrics for monitoring.

**No authentication required**

**Response (200):**
```
# HELP medlens_predictions_total Total predictions
# TYPE medlens_predictions_total counter
medlens_predictions_total 42

# HELP medlens_prediction_latency_seconds Prediction latency
# TYPE medlens_prediction_latency_seconds histogram
medlens_prediction_latency_seconds_bucket{le="0.05"} 20
medlens_prediction_latency_seconds_bucket{le="0.1"} 35
medlens_prediction_latency_seconds_bucket{le="+Inf"} 42
```

**cURL:**
```bash
curl http://localhost:8000/metrics
```

---

## Rate Limiting

The API implements rate limiting: **60 requests per 60 seconds per IP**.

**Response (429):**
```
Rate limit exceeded
```

---

## Common Error Responses

### Unauthorized (401)
```json
{
  "detail": "Invalid token"
}
```

### Forbidden (403)
```json
{
  "detail": "Insufficient role"
}
```

### Not Found (404)
```json
{
  "detail": "Not found"
}
```

### Unprocessable Entity (422)
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Example Workflows

### 1. Full Classification Workflow

```bash
# 1. Register or login
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }' | jq -r '.access_token')

# 2. Get current user info
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Upload a signal
RECORD_ID=$(curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@ecg_sample.wav" \
  -F "patient_id=patient_123" | jq -r '.id')

# 4. Classify the signal
curl -X POST http://localhost:8000/predict/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@ecg_sample.wav"

# 5. Detect anomalies
curl -X POST http://localhost:8000/anomaly/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@ecg_sample.wav"

# 6. View analytics (if doctor/admin role)
curl http://localhost:8000/analytics/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Batch Processing

```python
import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin"

# Login
response = requests.post(f"{API_URL}/auth/login", json={
    "username": USERNAME,
    "password": PASSWORD
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Process all WAV files in a directory
for wav_file in Path("signals").glob("*.wav"):
    with open(wav_file, "rb") as f:
        files = {"file": f}
        
        # Classify
        pred = requests.post(f"{API_URL}/predict/", headers=headers, files=files)
        pred_data = pred.json()
        
        # Detect anomalies
        f.seek(0)
        anom = requests.post(f"{API_URL}/anomaly/", headers=headers, files=files)
        anom_data = anom.json()
        
        # Store results
        print(f"{wav_file.name}: {pred_data['label']} ({pred_data['confidence']:.2%}) - Anomaly: {anom_data['is_anomaly']}")
```

---

## WebSocket Endpoints (Future)

```
ws://localhost:8000/ws/stream
```

Stream real-time predictions for continuous signal input.

---

## Swagger UI

Interactive API documentation available at:
```
http://localhost:8000/docs
```

---

## OpenAPI Schema

Full OpenAPI specification at:
```
http://localhost:8000/openapi.json
```

---

## Support

For issues or questions about the API, refer to `DOCUMENTATION.md` or open an issue on GitHub.
