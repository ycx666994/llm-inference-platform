from prometheus_client import Counter, Histogram


REQUESTS_TOTAL = Counter(
    "gateway_requests_total",
    "Total gateway requests",
    ["method", "path", "status_code"],
)

UPSTREAM_REQUESTS_TOTAL = Counter(
    "gateway_upstream_requests_total",
    "Total upstream vLLM requests",
    ["model", "status_code"],
)

REQUEST_LATENCY_SECONDS = Histogram(
    "gateway_request_latency_seconds",
    "Gateway request latency in seconds",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)
