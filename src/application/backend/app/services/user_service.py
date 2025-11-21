from app.db.models.user import DBUser
from app.schemas.db.user import User


def convert_db_user_to_user(db_user: DBUser) -> User:
    """Convert database user to Pydantic user model."""
    return User(
        username=db_user.username,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        disabled=not db_user.is_active,
        roles=[role.name for role in db_user.roles],
    )
