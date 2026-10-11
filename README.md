# Omniload

A concurrent HTTP load generator that accurately mitigates coordinated omission.

## Why this exists?

When performing load testing, naive implementations wait for one request to complete before sending the next, or dispatch based on the actual start time of the previous request. If the system under test slows down, the load generator ends up sending fewer requests (falling behind schedule). This artifact, known as "coordinated omission," results in overly optimistic latency percentiles because delayed responses prevent the load generator from seeing how the queue grows.

Omniload computes the *intended start time* of every request upfront. If a request is delayed because the system or network is overloaded, the latency is measured from when it *should* have started to when it actually completes, giving a realistic view of tail latency (p90, p99).

## Features

- Constant throughput load generation based on QPS.
- Accurate latency measurements via intended start time tracking.
- Output includes p50, p90, and p99 percentiles, plus success/error rates.
- Concurrent dispatch using `aiohttp` and `asyncio`.

## Installation

You can install `omniload` using `pip` or `uv`:

```bash
uv pip install omniload
```
Or for development:
```bash
uv venv
uv pip install -e .[dev]
```

## Usage

```bash
omniload --qps 100 --duration 10 http://localhost:8080/api/health
```

### Worked Example

Running a 10-second test against an endpoint at 50 QPS:

```bash
$ omniload --qps 50 --duration 10 http://example.com/
Starting load test on http://example.com/
Target QPS: 50.0, Duration: 10.0s
Total Requests: 500
Success Rate:   100.00%
Error Rate:     0.00%

Latency (ms) - Measured from Intended Start Time:
  p50: 42.15 ms
  p90: 55.30 ms
  p99: 104.12 ms
```

## Running the tests

```bash
pytest
```
