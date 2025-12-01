from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base, SCHEMA_NAME
from app.db.models.user import user_roles


class DBRole(Base):
    __tablename__ = "roles"
    __table_args__ = {'schema': SCHEMA_NAME} if SCHEMA_NAME else {}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship("DBUser", secondary=user_roles, back_populates="roles")
