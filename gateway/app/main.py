import time
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.auth import require_api_key
from app.config import get_settings
from app.metrics import REQUEST_LATENCY_SECONDS, REQUESTS_TOTAL, UPSTREAM_REQUESTS_TOTAL
from app.rate_limit import InMemoryRateLimiter

settings = get_settings()
limiter = InMemoryRateLimiter(max_requests=settings.rate_limit_per_minute)

app = FastAPI(title="LLM Inference Gateway", version="0.1.0")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - started_at
        route_path = request.scope.get("path", request.url.path)
        REQUEST_LATENCY_SECONDS.labels(request.method, route_path).observe(elapsed)
        REQUESTS_TOTAL.labels(request.method, route_path, str(status_code)).inc()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/chat/completions")
async def chat_completions(
    payload: dict[str, Any],
    api_key: str = Depends(require_api_key),
) -> Response:
    limiter.check(api_key)

    model = payload.get("model") or settings.default_model
    payload["model"] = model
    upstream_url = f"{settings.vllm_base_url.rstrip('/')}/v1/chat/completions"

    timeout = httpx.Timeout(settings.upstream_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            upstream_response = await client.post(upstream_url, json=payload)
        except httpx.RequestError as exc:
            UPSTREAM_REQUESTS_TOTAL.labels(model, "connection_error").inc()
            return JSONResponse(
                status_code=502,
                content={"detail": f"Upstream request failed: {exc.__class__.__name__}"},
            )

    UPSTREAM_REQUESTS_TOTAL.labels(model, str(upstream_response.status_code)).inc()

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        media_type=upstream_response.headers.get("content-type", "application/json"),
    )
