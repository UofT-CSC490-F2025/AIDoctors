from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
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
)

allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://main.d3jxl3jzen5r8m.amplifyapp.com",
    "http://aidoctors-alb-1329822649.us-east-1.elb.amazonaws.com"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(predictions.router)
