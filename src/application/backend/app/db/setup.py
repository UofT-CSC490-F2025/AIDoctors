from app.db.session import Base, engine, SessionLocal
from app.repositories.role_repository import create_role, get_role_by_name


def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create roles if they don't exist
    db = SessionLocal()
    if not get_role_by_name(db, "user"):
        create_role(db, "user", "Regular user")

    if not get_role_by_name(db, "admin"):
        create_role(db, "admin", "Administrator")

    if not get_role_by_name(db, "moderator"):
        create_role(db, "moderator", "Moderator")

    db.close()
