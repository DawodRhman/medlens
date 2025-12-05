from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict
from app.services.analytics_service import AnalyticsService
from app.utils.deps import require_role

router = APIRouter()

class AnalyticsResponse(BaseModel):
    metrics: Dict[str, Any]


@router.get("/", response_model=AnalyticsResponse, dependencies=[Depends(require_role("doctor"))])
def get_analytics():
    metrics = AnalyticsService.get_metrics()
    return {"metrics": metrics}
