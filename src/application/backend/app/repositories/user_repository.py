from typing import Optional
from sqlalchemy.orm import Session

from app.db.models.user import DBUser
from app.db.models.role import DBRole
from app.schemas.db.user import UserCreate
from app.config.security import password_hash_context


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[DBUser]:
    """Get all users with pagination."""
    return db.query(DBUser).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[DBUser]:
    """Get user by ID."""
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[DBUser]:
    """Get user by username."""
    return db.query(DBUser).filter(DBUser.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[DBUser]:
    """Get user by email."""
    return db.query(DBUser).filter(DBUser.email == email).first()


def create_user(db: Session, user: UserCreate) -> DBUser:
    """Create a new user."""
    hashed_password = password_hash_context.hash(user.password)

    db_user = DBUser(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
    )

    # Assign default user role
    user_role = db.query(DBRole).filter(DBRole.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
