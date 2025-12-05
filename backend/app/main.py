from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api import predict, anomaly, upload, analytics, auth
from app.middleware.rate_limit import RateLimitMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


app = FastAPI(title="MedLens API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiter middleware
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["anomaly"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get('/metrics')
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
