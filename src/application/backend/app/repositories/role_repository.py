from typing import Optional
from sqlalchemy.orm import Session

from app.db.models.role import DBRole


def get_role_by_name(db: Session, name: str) -> Optional[DBRole]:
    """Get role by name."""
    return db.query(DBRole).filter(DBRole.name == name).first()


def create_role(db: Session, name: str, description: str = "") -> DBRole:
    """Create a new role."""
    db_role = DBRole(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
