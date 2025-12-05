from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db.sql_models import SessionLocal, get_user_by_username, User
from app.utils.jwt import verify_token

security = HTTPBearer()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    username = payload.get('sub')
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def require_role(role: str):
    def _inner(user: User = Depends(get_current_user)):
        if user.role != role and user.role != 'admin':
            raise HTTPException(status_code=403, detail='Insufficient role')
        return user
    return _inner
