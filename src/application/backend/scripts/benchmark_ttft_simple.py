"""
Simple TTFT benchmark script that works without authentication.
Useful for quick local testing during development.

Usage:
    python scripts/benchmark_ttft_simple.py
"""

import asyncio
import time
import statistics
import httpx


async def measure_ttft():
    """Measure TTFT for a single request."""
    url = "http://localhost:8000/predict"
    payload = {
        "drug1": "ibuprofen",
        "drug2": "lisinopril",
        "Age": 65,
        "Sex": "M",
        "Comorbidities": ["Hypertension", "Diabetes"],
    }
    
    start = time.perf_counter()
    ttft = None
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            async with client.stream('POST', url, json=payload) as response:
                async for chunk in response.aiter_bytes():
                    if ttft is None:
                        ttft = time.perf_counter() - start
                
                total = time.perf_counter() - start
                return {
                    "ttft": ttft,
                    "total": total,
                    "status": response.status_code,
                    "success": response.status_code == 200
                }
        except Exception as e:
            return {
                "ttft": None,
                "total": time.perf_counter() - start,
                "status": None,
                "success": False,
                "error": str(e)
            }


async def main():
    """Run 10 benchmark iterations and print statistics."""
    print("Running TTFT Benchmark (10 iterations)...\n")
    
    results = []
    for i in range(10):
        result = await measure_ttft()
        results.append(result)
        
        if result["success"]:
            print(f"Run {i+1:2d}: TTFT={result['ttft']:.3f}s  Total={result['total']:.3f}s")
        else:
            print(f"Run {i+1:2d}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Calculate statistics
    successful = [r for r in results if r["success"]]
    
    if not successful:
        print("\nAll requests failed!")
        return
    
    ttft_times = [r["ttft"] for r in successful]
    total_times = [r["total"] for r in successful]
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"\nTTFT (Time to First Token):")
    print(f"  Mean:   {statistics.mean(ttft_times):.3f}s")
    print(f"  Median: {statistics.median(ttft_times):.3f}s")
    print(f"  Min:    {min(ttft_times):.3f}s")
    print(f"  Max:    {max(ttft_times):.3f}s")
    
    print(f"\nTotal Time:")
    print(f"  Mean:   {statistics.mean(total_times):.3f}s")
    print(f"  Median: {statistics.median(total_times):.3f}s")
    
    print(f"\nSuccess Rate: {len(successful)}/10 ({len(successful)*10}%)")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
