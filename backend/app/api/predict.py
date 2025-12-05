from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from app.services.predict_service import PredictService
from app.utils.deps import require_role

router = APIRouter()

class PredictResponse(BaseModel):
    label: str
    confidence: float


@router.post("/", response_model=PredictResponse, dependencies=[Depends(require_role("technician"))])
async def predict_signal(file: UploadFile = File(...)):
    data = await file.read()
    # service will handle parsing bytes into signal
    try:
        label, conf = PredictService.predict_from_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"label": label, "confidence": conf}
