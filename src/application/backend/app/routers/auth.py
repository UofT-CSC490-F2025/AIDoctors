from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.dependencies import get_db
from app.services.auth_service import authenticate_user, create_access_token
from app.config.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Store token in an httpOnly cookie for frontend auth
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True,
        max_age=int(access_token_expires.total_seconds()),
        samesite="lax",
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def clear_access_token_cookie(
    response: Response,
):
    """Clear the access token cookie to log out the user."""
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return {"detail": "Successfully logged out."}
