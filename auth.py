from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, Header, HTTPException, status
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from config import settings
from db import get_db
from db_models import User

AUTH_ERROR = {"message": "인증 에러"}


def create_jwt_token(user_id: str) -> str:
    payload = {
        "id": user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(seconds=settings.jwt_expires_sec),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def hash_password(password: str) -> str:
    return bcrypt.using(rounds=settings.bcrypt_salt_rounds).hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)


def get_current_user_context(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not (authorization and authorization.startswith("Bearer ")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_ERROR)

    token = authorization.split(" ", 1)[1].strip()
    try:
        decoded = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_ERROR)

    user_id = decoded.get("id")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_ERROR)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_ERROR)

    return {"user": user, "token": token}
