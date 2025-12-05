from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.utils.jwt import create_access_token, verify_password, get_password_hash
from app.utils.deps import get_db, get_current_user
from app.db.sql_models import get_user_by_username, create_user

router = APIRouter()


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=AuthResponse)
def register(data: AuthRequest, db=Depends(get_db)):
    existing = get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="User exists")
    hashed = get_password_hash(data.password)
    user = create_user(db, data.username, hashed, role='technician')
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token}


@router.post("/login", response_model=AuthResponse)
def login(data: AuthRequest, db=Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"username": user.username, "role": user.role}
