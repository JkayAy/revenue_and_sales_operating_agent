from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request
from starlette.responses import JSONResponse

from sales_api.config import settings

# ip -> timestamps (seconds)
_hits: dict[str, list[float]] = defaultdict(list)

INGEST_PATHS = {"/v1/leads/ingest", "/v1/webhooks/hubspot"}


def client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def allow_request(key: str) -> bool:
    limit = settings.rate_limit_per_minute
    window = 60.0
    now = time.time()
    bucket = _hits[key]
    bucket[:] = [t for t in bucket if now - t < window]
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in INGEST_PATHS and request.method == "POST":
        if not allow_request(client_key(request)):
            return JSONResponse(
                status_code=429,
                content={"detail": "rate_limit_exceeded"},
                headers={"Retry-After": "60"},
            )
    return await call_next(request)
