from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.security import (
    ACCESS_TOKEN_SECRET_KEY,
    ACCESS_TOKEN_ALGORITHM,
    oauth2_scheme,
)
from app.db.session import SessionLocal
from app.repositories.user_repository import get_user_by_username
from app.schemas.db.user import User
from app.services.user_service import convert_db_user_to_user


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_from_access_token(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise credentials_exception
    return convert_db_user_to_user(db_user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user_from_access_token),
):
    """Get the current active user (not disabled)."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
