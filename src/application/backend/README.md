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

### 3. Run the Server

```bash
uv run uvicorn main:app --reload
```

Or activate the virtual environment and run directly:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload
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
├── main.py              # Main FastAPI application
├── config.py            # Configuration settings
├── pyproject.toml       # Python dependencies (uv)
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Development

### Quick Reference

Common `uv` commands:

```bash
# Install dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv sync --upgrade

# Run a command in the virtual environment
uv run <command>
```

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
from routers import example

app.include_router(example.router)
```

### Adding Database Support

1. Add database dependencies to `pyproject.toml` (e.g., SQLAlchemy, asyncpg):
    ```bash
    uv add sqlalchemy asyncpg
    ```
2. Create database models in `models/`
3. Create database connection in `database.py`
4. Add database URL to `.env`

## Testing

```bash
# Install dev dependencies (includes testing tools)
uv sync --all-extras

# Run tests
uv run pytest
```
