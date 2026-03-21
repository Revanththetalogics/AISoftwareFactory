"""
Performance tester for Simulation module.

This module provides load testing and performance measurement
for generated applications.
"""

import asyncio
import time
from dataclasses import dataclass
from statistics import mean, median
from typing import Any, Callable, Dict, List

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceResult:
    """Performance test result."""
    operation: str
    requests: int
    total_time: float
    avg_latency: float
    median_latency: float
    min_latency: float
    max_latency: float
    p95_latency: float
    p99_latency: float
    errors: int
    throughput: float  # requests per second


class PerformanceTester:
    """
    Performance tester for load testing.

    Provides concurrent request generation and latency measurement
    for performance validation.
    """

    def __init__(self):
        """Initialize the performance tester."""
        self._logger = get_logger(__name__)

    async def load_test(
        self,
        operation: Callable,
        requests: int = 100,
        concurrency: int = 10,
        *args,
        **kwargs
    ) -> PerformanceResult:
        """
        Run a load test.

        Args:
            operation: Async function to test
            requests: Total number of requests
            concurrency: Concurrent requests
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Performance test results
        """
        latencies = []
        errors = 0

        start_time = time.time()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)

        async def make_request():
            nonlocal errors
            async with semaphore:
                req_start = time.time()
                try:
                    await operation(*args, **kwargs)
                    latency = time.time() - req_start
                    latencies.append(latency)
                except Exception as e:
                    errors += 1
                    self._logger.warning("Request failed", error=str(e))

        # Run all requests
        tasks = [make_request() for _ in range(requests)]
        await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        if not latencies:
            return PerformanceResult(
                operation=operation.__name__,
                requests=requests,
                total_time=total_time,
                avg_latency=0,
                median_latency=0,
                min_latency=0,
                max_latency=0,
                p95_latency=0,
                p99_latency=0,
                errors=errors,
                throughput=0
            )

        # Calculate statistics
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        return PerformanceResult(
            operation=operation.__name__,
            requests=requests,
            total_time=total_time,
            avg_latency=mean(latencies),
            median_latency=median(latencies),
            min_latency=min(latencies),
            max_latency=max(latencies),
            p95_latency=sorted_latencies[int(n * 0.95)],
            p99_latency=sorted_latencies[int(n * 0.99)],
            errors=errors,
            throughput=requests / total_time
        )

    async def benchmark_api(
        self,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        duration: int = 60
    ) -> Dict[str, PerformanceResult]:
        """
        Benchmark API endpoints.

        Args:
            base_url: Base URL for API
            endpoints: List of endpoint configurations
            duration: Test duration in seconds

        Returns:
            Results per endpoint
        """
        results = {}

        for endpoint in endpoints:
            name = endpoint["name"]
            method = endpoint.get("method", "GET")
            path = endpoint["path"]

            # Create test function
            async def test_fn():
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"{base_url}{path}"
                    async with session.request(method, url) as resp:
                        await resp.text()

            # Run load test
            result = await self.load_test(
                test_fn,
                requests=100,
                concurrency=10
            )

            results[name] = result

        return results

    def generate_report(self, results: Dict[str, PerformanceResult]) -> Dict[str, Any]:
        """Generate performance test report."""
        report = {
            "summary": {
                "total_tests": len(results),
                "total_requests": sum(r.requests for r in results.values()),
                "total_errors": sum(r.errors for r in results.values()),
                "avg_throughput": mean(r.throughput for r in results.values())
            },
            "details": {}
        }

        for name, result in results.items():
            report["details"][name] = {
                "requests": result.requests,
                "avg_latency_ms": round(result.avg_latency * 1000, 2),
                "p95_latency_ms": round(result.p95_latency * 1000, 2),
                "throughput_rps": round(result.throughput, 2),
                "errors": result.errors
            }

        return report
