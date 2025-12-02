"""
Benchmark script for measuring Time To First Token (TTFT) for the predict endpoint.

This script measures:
1. Time to first byte (TTFB) - network latency + server processing until first response
2. Total request time
3. Statistics across multiple runs

Usage:
    python scripts/benchmark_ttft.py --url http://localhost:8000 --runs 10
"""

import argparse
import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx
import json
from datetime import datetime


def create_sample_request() -> Dict[str, Any]:
    """
    Create a sample prediction request payload.
    Modify this to test different scenarios.
    """
    return {
        "patient_uuid": "benchmark-patient",
        "drug1": "ibuprofen",
        "drug2": "lisinopril",
        "Age": 65,
        "Sex": "M",
        "Comorbidities": ["Hypertension", "Diabetes"],
    }


async def measure_ttft_single(
    client: httpx.AsyncClient,
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str]
) -> Dict[str, float]:
    """
    Measure TTFT for a single request.
    
    Returns:
        Dict with timing metrics:
        - ttft: Time to first token (first byte received)
        - total_time: Total request duration
        - status_code: HTTP status code
    """
    start_time = time.perf_counter()
    ttft = None
    
    try:
        async with client.stream('POST', url, json=payload, headers=headers) as response:
            # Time when we receive the first byte
            async for chunk in response.aiter_bytes():
                if ttft is None:
                    ttft = time.perf_counter() - start_time
                # Continue reading to get total time
                pass
            
            total_time = time.perf_counter() - start_time
            
            return {
                "ttft": ttft,
                "total_time": total_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
    except Exception as e:
        return {
            "ttft": None,
            "total_time": time.perf_counter() - start_time,
            "status_code": None,
            "success": False,
            "error": str(e)
        }


async def run_benchmark(
    base_url: str,
    num_runs: int,
    token: str = None,
    concurrent: int = 1,
    warmup_runs: int = 1
) -> Dict[str, Any]:
    """
    Run TTFT benchmark with multiple iterations.
    
    Args:
        base_url: Base URL of the API (e.g., http://localhost:8000)
        num_runs: Number of benchmark iterations
        token: Optional authentication token
        concurrent: Number of concurrent requests (default: 1 for sequential)
        warmup_runs: Number of warmup runs to exclude from stats
    
    Returns:
        Dictionary with benchmark results and statistics
    """
    url = f"{base_url}/predict"
    payload = create_sample_request()
    
    headers = {
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"Starting TTFT Benchmark")
    print(f"   URL: {url}")
    print(f"   Runs: {num_runs} (+ {warmup_runs} warmup)")
    print(f"   Concurrent: {concurrent}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Warmup runs
        if warmup_runs > 0:
            print(f"\nWarmup ({warmup_runs} runs)...")
            for i in range(warmup_runs):
                result = await measure_ttft_single(client, url, payload, headers)
                if result["success"]:
                    print(f"   Warmup {i+1}: TTFT={result['ttft']:.3f}s, Total={result['total_time']:.3f}s")
                else:
                    print(f"   Warmup {i+1}: FAILED - {result.get('error', 'Unknown error')}")
        
        # Actual benchmark runs
        print(f"\nBenchmark ({num_runs} runs)...")
        results: List[Dict[str, float]] = []
        
        if concurrent == 1:
            # Sequential execution
            for i in range(num_runs):
                result = await measure_ttft_single(client, url, payload, headers)
                results.append(result)
                
                if result["success"]:
                    print(f"   Run {i+1}/{num_runs}: TTFT={result['ttft']:.3f}s, Total={result['total_time']:.3f}s")
                else:
                    print(f"   Run {i+1}/{num_runs}: FAILED - {result.get('error', 'Unknown error')}")
        else:
            # Concurrent execution
            tasks = []
            for i in range(num_runs):
                task = measure_ttft_single(client, url, payload, headers)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            for i, result in enumerate(results):
                if result["success"]:
                    print(f"   Run {i+1}/{num_runs}: TTFT={result['ttft']:.3f}s, Total={result['total_time']:.3f}s")
                else:
                    print(f"   Run {i+1}/{num_runs}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Calculate statistics
    successful_results = [r for r in results if r["success"]]
    failed_count = len(results) - len(successful_results)
    
    if not successful_results:
        return {
            "success": False,
            "error": "All requests failed",
            "failed_count": failed_count,
            "total_runs": num_runs
        }
    
    ttft_times = [r["ttft"] for r in successful_results]
    total_times = [r["total_time"] for r in successful_results]
    
    stats = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "url": url,
            "num_runs": num_runs,
            "warmup_runs": warmup_runs,
            "concurrent": concurrent,
        },
        "ttft": {
            "mean": statistics.mean(ttft_times),
            "median": statistics.median(ttft_times),
            "min": min(ttft_times),
            "max": max(ttft_times),
            "stdev": statistics.stdev(ttft_times) if len(ttft_times) > 1 else 0,
            "p95": sorted(ttft_times)[int(len(ttft_times) * 0.95)] if len(ttft_times) > 1 else ttft_times[0],
            "p99": sorted(ttft_times)[int(len(ttft_times) * 0.99)] if len(ttft_times) > 1 else ttft_times[0],
        },
        "total_time": {
            "mean": statistics.mean(total_times),
            "median": statistics.median(total_times),
            "min": min(total_times),
            "max": max(total_times),
            "stdev": statistics.stdev(total_times) if len(total_times) > 1 else 0,
        },
        "success_rate": len(successful_results) / num_runs * 100,
        "failed_count": failed_count,
        "raw_results": results
    }
    
    return stats


def print_results(stats: Dict[str, Any]):
    """Print formatted benchmark results."""
    if not stats["success"]:
        print(f"\nBenchmark failed: {stats.get('error')}")
        return
    
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    
    print(f"\nTime to First Token (TTFT):")
    print(f"   Mean:     {stats['ttft']['mean']:.3f}s")
    print(f"   Median:   {stats['ttft']['median']:.3f}s")
    print(f"   Min:      {stats['ttft']['min']:.3f}s")
    print(f"   Max:      {stats['ttft']['max']:.3f}s")
    print(f"   Std Dev:  {stats['ttft']['stdev']:.3f}s")
    print(f"   P95:      {stats['ttft']['p95']:.3f}s")
    print(f"   P99:      {stats['ttft']['p99']:.3f}s")
    
    print(f"\nTotal Request Time:")
    print(f"   Mean:     {stats['total_time']['mean']:.3f}s")
    print(f"   Median:   {stats['total_time']['median']:.3f}s")
    print(f"   Min:      {stats['total_time']['min']:.3f}s")
    print(f"   Max:      {stats['total_time']['max']:.3f}s")
    print(f"   Std Dev:  {stats['total_time']['stdev']:.3f}s")
    
    print(f"\nSuccess Rate: {stats['success_rate']:.1f}%")
    if stats['failed_count'] > 0:
        print(f"Failed Requests: {stats['failed_count']}")
    
    print("\n" + "=" * 60)


def save_results(stats: Dict[str, Any], output_file: str):
    """Save benchmark results to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nResults saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Time To First Token (TTFT) for the predict endpoint"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of benchmark runs (default: 10)"
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Number of warmup runs (default: 1)"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent requests (default: 1 for sequential)"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Authentication token (optional)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for results (JSON format, optional)"
    )
    
    args = parser.parse_args()
    
    # Run benchmark
    stats = asyncio.run(run_benchmark(
        base_url=args.url,
        num_runs=args.runs,
        token=args.token,
        concurrent=args.concurrent,
        warmup_runs=args.warmup
    ))
    
    # Print results
    print_results(stats)
    
    # Save results if output file specified
    if args.output:
        save_results(stats, args.output)


if __name__ == "__main__":
    main()
