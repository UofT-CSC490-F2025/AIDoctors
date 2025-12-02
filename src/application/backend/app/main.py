from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.db import setup
from app.routers import predictions, users, auth
from app.utils.exception_handlers import validation_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI application...")
    setup.init_db()

    yield

    # Shutdown
    print("Shutting down FastAPI application...")


app = FastAPI(
    title="CSC490 API",
    description="FastAPI backend for CSC490 project",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,  # Disable automatic redirects to prevent mixed content errors with CloudFront
)

allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://main.d3jxl3jzen5r8m.amplifyapp.com",
]

# Configure CORS for cookie-based authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Enable credentials for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow CloudFront distribution
    allow_origin_regex=r"https://.*\.cloudfront\.net",
)


# Register custom exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AIDoctors API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Create API router with /api prefix
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(predictions.router)

app.include_router(api_router)
