FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv
RUN uv sync --frozen

# Copy application code
COPY ./app ./app

# Create directory for SQLite database and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Set environment variable for database path
ENV DATABASE_URL=sqlite:///./data/test.db

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]