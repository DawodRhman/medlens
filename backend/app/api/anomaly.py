from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.services.anomaly_service import AnomalyService

router = APIRouter()

class AnomalyResponse(BaseModel):
    score: float
    is_anomaly: bool


@router.post("/", response_model=AnomalyResponse)
async def detect_anomaly(file: UploadFile = File(...)):
    data = await file.read()
    try:
        score, is_anom = AnomalyService.detect_from_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"score": score, "is_anomaly": is_anom}
