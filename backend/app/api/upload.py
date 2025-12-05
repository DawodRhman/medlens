from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
from app.db import storage

router = APIRouter()


class UploadResponse(BaseModel):
    id: str
    message: str


@router.post("/", response_model=UploadResponse)
async def upload_signal(file: UploadFile = File(...), patient_id: Optional[str] = Form(None)):
    data = await file.read()
    record_id = storage.save_raw_signal(data, metadata={"patient_id": patient_id})
    return {"id": record_id, "message": "uploaded"}
