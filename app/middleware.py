import time

from fastapi import Request
from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of HTTP requests",
    ["method", "status"],
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method"],
)


async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    if request.url.path != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
        ).observe(duration)

    print(f"{request.method} {request.url.path} {response.status_code} {duration:.4f}s")

    return response
