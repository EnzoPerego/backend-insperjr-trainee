"""
Utilitários para criação e validação de JWT
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import os
import jwt


def get_jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "change-me-in-env")


def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


def get_jwt_expires_minutes() -> int:
    try:
        return int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    except Exception:
        return 60


def create_access_token(subject: str, claims: Dict[str, Any]) -> str:
    to_encode = {"sub": subject, **claims}
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=get_jwt_expires_minutes())
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, get_jwt_secret(), algorithm=get_jwt_algorithm())
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
        return decoded
    except Exception:
        return None


