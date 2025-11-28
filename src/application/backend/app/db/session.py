from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import boto3
import json


load_dotenv()

def get_db_credentials():
    """Fetch database connection details from SSM and Secrets Manager"""
    
    try:
        ssm = boto3.client("ssm")
        secrets = boto3.client("secretsmanager")
        
        # Get connection details from SSM Parameter Store
        host = ssm.get_parameter(Name="/aidoctors/db/host")["Parameter"]["Value"]
        port = ssm.get_parameter(Name="/aidoctors/db/port")["Parameter"]["Value"]
        user = ssm.get_parameter(Name="/aidoctors/db/user")["Parameter"]["Value"]
        dbname = ssm.get_parameter(Name="/aidoctors/db/name")["Parameter"]["Value"]
        schema = ssm.get_parameter(Name="/aidoctors/db/schema")["Parameter"]["Value"]
        
        # Get the secret ARN from SSM
        secret_arn = ssm.get_parameter(Name="/aidoctors/db/password-secret-arn")["Parameter"]["Value"]
        
        # Get password from Secrets Manager (RDS managed secret)
        secret_value = secrets.get_secret_value(SecretId=secret_arn)
        secret_dict = json.loads(secret_value["SecretString"])
        password = secret_dict["password"]
        
        return host, port, user, password, dbname, schema
    except Exception as e:
        print(f"❌ Failed to fetch AWS credentials: {e}")
        raise


# Check if we're in testing mode or should use local database
is_testing = os.getenv("TESTING") == "true"

if is_testing:
    # Use SQLite for testing or local development
    print("Using local SQLite database")
    DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Try to connect to AWS RDS
    print("🔧 Configuring AWS RDS database connection...")
    try:
        host, port, user, password, dbname, schema = get_db_credentials()
        DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?options=-csearch_path%3D{schema}"
        
        # PostgreSQL-specific engine configuration
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False  # Set to True for SQL debugging
        )
        print(f"AWS RDS connection configured: {host}:{port}/{dbname}")

    except Exception as e:
        print(f"AWS RDS configuration failed: {e}")
        
        DATABASE_URL = "sqlite:///./app.db"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
