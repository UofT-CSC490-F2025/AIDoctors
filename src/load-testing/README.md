# Load Testing with Locust

This directory contains load testing scripts for the CSC490 FastAPI backend using [Locust](https://locust.io/).

## Setup

### Install Locust

```bash
uv add locust
```

## Running Load Tests

### 1. Start your backend server

Make sure your FastAPI backend is running:

```bash
cd ../application/backend
uv run uvicorn app.main:app --reload
```

### 2. Run Locust

From this directory:

```bash
locust -f locustfile.py --host=http://localhost:8000
```

### 3. Access the Web UI

Open your browser to: **http://localhost:8089**

Configure:

-   **Number of users**: Total users to simulate (e.g., 10, 50, 100)
-   **Spawn rate**: Users spawned per second (e.g., 5)
-   **Host**: http://localhost:8000 (pre-filled if you used --host flag)

Click **Start swarming** to begin the test.

## Test Scenarios

### APIUser (Authenticated Users)

Simulates authenticated users performing various tasks:

-   **Health checks** (50% of requests) - Lightweight monitoring
-   **Root endpoint** (30% of requests) - Basic API access
-   **User profile access** (20% of requests) - Fetching user data
-   **DDI Predictions** (10% of requests) - Resource-intensive Bedrock API calls

Each user:

1. Registers with unique credentials
2. Authenticates to get JWT token
3. Performs weighted random tasks
4. Waits 1-3 seconds between requests

### UnauthenticatedUser

Simulates public/unauthenticated traffic:

-   **Health checks** (60% of requests)
-   **Root endpoint** (30% of requests)
-   **Unauthorized access attempts** (10% of requests) - Tests auth validation

## Command Line Options

### Basic Usage

```bash
# Run with web UI
locust -f locustfile.py --host=http://localhost:8000

# Run headless (no web UI)
locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 60s

# Run specific user class only
locust -f locustfile.py --host=http://localhost:8000 APIUser
```

## Interpreting Results

### Key Metrics

-   **RPS (Requests Per Second)**: Throughput of your API
-   **Response Time**: 50th, 95th, 99th percentiles
-   **Failure Rate**: Percentage of failed requests
-   **Users**: Number of concurrent simulated users

## Testing Strategies

### Smoke Test

Quick sanity check with minimal load:

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 5 -r 1 -t 30s
```

### Load Test

Simulate expected production traffic:

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 5m
```

### Stress Test

Find breaking point:

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 200 -r 10 -t 10m
```

### Spike Test

Sudden traffic surge:

```bash
locust -f locustfile.py --host=http://localhost:8000 --headless -u 100 -r 50 -t 2m
```

## Troubleshooting

### Connection Refused

-   Ensure backend is running on the correct port
-   Check firewall settings

### High Failure Rate

-   Check backend logs for errors
-   Verify database is accessible
-   Check AWS credentials for Bedrock

### Slow Response Times

-   Monitor backend CPU/memory usage
-   Check database query performance
-   Review Bedrock API latency

## Resources

-   [Locust Documentation](https://docs.locust.io/)
-   [Writing Locustfiles](https://docs.locust.io/en/stable/writing-a-locustfile.html)
-   [Distributed Load Testing](https://docs.locust.io/en/stable/running-distributed.html)
