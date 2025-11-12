from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: Optional[list[str]] = None


class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
