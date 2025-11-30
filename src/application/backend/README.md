# FastAPI Backend

A FastAPI backend for the CSC490 project.

## Setup

### Prerequisites

Install [uv](https://github.com/astral-sh/uv):

### 1. Install Dependencies

```bash
uv sync
```

This will create a virtual environment and install all dependencies.

### 2. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

#### Environment Variable: `ENVIRONMENT`

The `ENVIRONMENT` variable controls which database and configuration sources the application uses:

-   **`testing`**: Uses local SQLite database (`sqlite:///./test.db`) and local environment variables. Used in CI/CD testing workflows.
-   **`development`**: Uses local SQLite database and local environment variables. Recommended for local development.
-   **`production`**: Uses AWS RDS for the database and fetches secrets from AWS Systems Manager (SSM) and Secrets Manager. Used in deployed environments.

### 3. Configure AWS Bedrock

The application uses AWS Bedrock for drug-drug interaction predictions.

**For local testing:**

-   Set your AWS credentials in the `.env` file:
    ```
    AWS_ACCESS_KEY_ID=your-access-key
    AWS_SECRET_ACCESS_KEY=your-secret-key
    AWS_REGION=us-east-1
    BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
    ```

**For ECS deployment:**

-   No credentials needed in `.env`
-   The ECS task will automatically inherit IAM role permissions
-   Ensure the task role has `bedrock:InvokeModel` permission

### 4. Run the Server

```bash
uv run uvicorn app.main:app --reload
```

Or activate the virtual environment and run directly:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

-   **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
-   **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
-   **OpenAPI schema**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/                            # Main FastAPI application package
│   ├── main.py                     # Creates FastAPI app, mounts routers, middleware, handlers
│   ├── dependencies.py             # Shared dependencies injected with Depends()
│
│   ├── core/                       # Global configuration and security
│   │   ├── config.py               # Environment variables and settings via Pydantic
│   │   ├── security.py             # Password hashing, JWT, OAuth2 logic
│   │   ├── exceptions.py           # Custom exceptions and FastAPI handlers
│   │   └── logging_config.py       # Logging setup and formatters
│
│   ├── db/                         # Database engine, session, ORM models
│   │   ├── session.py              # Engine, SessionLocal, Base declarations
│   │   ├── models/                 # SQLAlchemy models for tables
│   │   └── setup.py                # Creates and seeds the database
│
│   ├── schemas/                    # Pydantic models for request/response validation
│
│   ├── repositories/               # CRUD and persistence logic
│
│   ├── services/                   # Business/domain logic combining repositories and APIs
│
│   ├── routers/                    # HTTP route definitions grouped by domain
│
│   ├── external_services/          # Integrations with third-party APIs (e.g. AWS)
│
│   └── utils/                      # Generic helper functions (validation, formatting, etc.)
│
├── migrations/                     # Alembic migration scripts for schema versioning
│   └── env.py
│
├── tests/                          # Automated tests
│
├── .env.example                    # Example environment variables
├── alembic.ini                     # Alembic configuration
├── .gitignore                      # Files and folders ignored by Git
├── pyproject.toml                  # Python dependencies (uv)
└── README.md                       # Project documentation and usage guide

```

## Development

### Adding New Routes

Create new route files in a `routers/` directory:

```python
# routers/example.py
from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/")
async def get_examples():
    return {"examples": []}
```

Then import and include in `main.py`:

```python
from app.routers import example

app.include_router(example.router)
```

## Testing

```bash
# Install dev dependencies (includes testing tools)
uv sync --all-extras

# Run tests
uv run pytest
```

### GitHub Actions

The repository includes a GitHub Actions workflow for running tests:

-   `backend_test.yaml`: Runs `uv run pytest` and comments the results on the PR.
