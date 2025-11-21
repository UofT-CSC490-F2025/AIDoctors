from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_username
from app.config.security import (
    ACCESS_TOKEN_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ACCESS_TOKEN_SECRET_KEY,
    password_hash_context,
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not password_hash_context.verify(password, user.hashed_password):
        return False
    return user
