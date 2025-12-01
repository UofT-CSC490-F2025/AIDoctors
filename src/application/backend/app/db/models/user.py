from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base, SCHEMA_NAME


# Association table for many-to-many relationship between users and roles
# Build ForeignKey references conditionally based on schema
if SCHEMA_NAME:
    user_fk = f"{SCHEMA_NAME}.users.id"
    role_fk = f"{SCHEMA_NAME}.roles.id"
else:
    user_fk = "users.id"
    role_fk = "roles.id"

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey(user_fk)),
    Column("role_id", Integer, ForeignKey(role_fk)),
    schema=SCHEMA_NAME
)


class DBUser(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME else {}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    roles = relationship("DBRole", secondary=user_roles, back_populates="users")
