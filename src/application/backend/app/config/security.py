from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import os
from dotenv import load_dotenv


load_dotenv()

ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_COOKIE_NAME = "access_token"

# Allow missing Authorization header so we can fall back to cookies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)
password_hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
