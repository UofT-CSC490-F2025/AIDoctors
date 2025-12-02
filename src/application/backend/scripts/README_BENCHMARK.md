# TTFT Benchmark Script

This script measures **Time To First Token (TTFT)** for the `/predict` endpoint, which is a critical performance metric for LLM-based APIs.

## What is TTFT?

Time To First Token (TTFT) measures the time from when a request is sent until the first byte of the response is received. This is particularly important for streaming responses and user experience, as it represents the perceived latency before the user sees any output.

## Installation

The script requires `httpx` for async HTTP requests:

```bash
# If using uv (recommended)
uv pip install httpx

# Or with pip
pip install httpx
```

## Usage

### Basic Usage

Run 10 benchmark iterations against a local server:

```bash
python scripts/benchmark_ttft.py --url http://localhost:8000 --runs 10
```

### With Authentication

If your endpoint requires authentication:

```bash
python scripts/benchmark_ttft.py \
  --url http://localhost:8000 \
  --runs 10 \
  --token "your-jwt-token-here"
```

### Advanced Options

```bash
python scripts/benchmark_ttft.py \
  --url http://localhost:8000 \
  --runs 20 \
  --warmup 3 \
  --concurrent 5 \
  --output results.json
```

## Command Line Arguments

| Argument       | Default                 | Description                                    |
| -------------- | ----------------------- | ---------------------------------------------- |
| `--url`        | `http://localhost:8000` | Base URL of the API                            |
| `--runs`       | `10`                    | Number of benchmark iterations                 |
| `--warmup`     | `1`                     | Number of warmup runs (excluded from stats)    |
| `--concurrent` | `1`                     | Number of concurrent requests (1 = sequential) |
| `--token`      | `None`                  | Authentication token (optional)                |
| `--output`     | `None`                  | Output file for JSON results (optional)        |
