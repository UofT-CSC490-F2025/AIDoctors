from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "CSC490 API"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
