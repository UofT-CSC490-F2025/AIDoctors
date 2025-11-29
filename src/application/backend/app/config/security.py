from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import boto3
import os

secret_token = None
try:
    # Only attempt AWS fetch if not in test mode
    if os.getenv("TESTING") != "true":
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        ssm = boto3.client("ssm", region_name=aws_region)
        secret_token = ssm.get_parameter(Name="/aidoctors/access-token-secret")["Parameter"]["Value"]
except Exception as e:
    print(f"Failed to fetch AWS credentials: {e}")

# Fallback to environment variable or test default
if not secret_token:
    secret_token = os.getenv("ACCESS_TOKEN_SECRET_KEY")

ACCESS_TOKEN_SECRET_KEY = secret_token
ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_COOKIE_NAME = "access_token"

# Allow missing Authorization header so we can fall back to cookies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)
password_hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
