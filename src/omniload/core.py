import asyncio
import time
from dataclasses import dataclass
from typing import List

import aiohttp
import numpy as np


@dataclass
class RequestResult:
    intended_start_time: float
    actual_start_time: float
    completion_time: float
    status: int
    error: str = ""

    @property
    def latency(self) -> float:
        # Measure latency from intended start time to mitigate coordinated omission
        return self.completion_time - self.intended_start_time


class LoadGenerator:
    def __init__(self, url: str, qps: float, duration: float):
        self.url = url
        self.qps = qps
        self.duration = duration
        self.total_requests = int(qps * duration)
        self.results: List[RequestResult] = []

    async def _make_request(
        self, session: aiohttp.ClientSession, intended_start_time: float
    ):
        actual_start = time.monotonic()
        status = 0
        error_msg = ""
        try:
            async with session.get(self.url) as response:
                status = response.status
                await response.read()
        except Exception as e:
            error_msg = str(e)
            
        completion_time = time.monotonic()
        
        self.results.append(
            RequestResult(
                intended_start_time=intended_start_time,
                actual_start_time=actual_start,
                completion_time=completion_time,
                status=status,
                error=error_msg,
            )
        )

    async def run(self):
        # We use a custom connector with a higher limit since we're generating load.
        connector = aiohttp.TCPConnector(limit=0)
        async with aiohttp.ClientSession(connector=connector) as session:
            start_time = time.monotonic()
            tasks = []
            
            for i in range(self.total_requests):
                intended_start = start_time + (i / self.qps)
                now = time.monotonic()
                
                if intended_start > now:
                    await asyncio.sleep(intended_start - now)
                
                # We spawn the task and keep the reference
                task = asyncio.create_task(self._make_request(session, intended_start))
                tasks.append(task)
                
            # Wait for all remaining requests to finish
            if tasks:
                await asyncio.gather(*tasks)

        return self.results


def print_summary(results: List[RequestResult]):
    if not results:
        print("No results to summarize.")
        return

    latencies = [r.latency * 1000 for r in results]  # convert to ms
    successes = [r for r in results if r.status >= 200 and r.status < 400]
    errors = [r for r in results if r.status < 200 or r.status >= 400 or r.error]
    
    total = len(results)
    success_rate = (len(successes) / total) * 100
    error_rate = (len(errors) / total) * 100
    
    p50 = np.percentile(latencies, 50)
    p90 = np.percentile(latencies, 90)
    p99 = np.percentile(latencies, 99)
    
    print(f"Total Requests: {total}")
    print(f"Success Rate:   {success_rate:.2f}%")
    print(f"Error Rate:     {error_rate:.2f}%")
    print("\nLatency (ms) - Measured from Intended Start Time:")
    print(f"  p50: {p50:.2f} ms")
    print(f"  p90: {p90:.2f} ms")
    print(f"  p99: {p99:.2f} ms")
