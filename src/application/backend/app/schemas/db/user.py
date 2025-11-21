from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    username: str = Field(examples=["johndoe"])
    email: Optional[str] = Field(default=None, examples=["john.doe@mail.utoronto.ca"])
    first_name: Optional[str] = Field(default=None, examples=["John"])
    last_name: Optional[str] = Field(default=None, examples=["Doe"])
    disabled: Optional[bool] = Field(default=None, examples=[False])
    roles: Optional[list[str]] = Field(default=None, examples=[["user"]])


class UserCreate(BaseModel):
    username: str = Field(examples=["johndoe"])
    email: str = Field(examples=["john.doe@mail.utoronto.ca"])
    first_name: str = Field(examples=["John"])
    last_name: str = Field(examples=["Doe"])
    password: str = Field(examples=["SecurePassword123!"])
