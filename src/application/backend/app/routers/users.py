from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_active_user, get_db
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.db.user import User, UserCreate


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db=db, user=user)
    return User(
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        disabled=not new_user.is_active,
        roles=[role.name for role in new_user.roles],
    )


@router.get("/me", response_model=User)
async def get_logged_in_user(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user
