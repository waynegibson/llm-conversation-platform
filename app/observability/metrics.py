from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "llm_platform_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "llm_platform_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)
CHAT_REQUESTS = Counter(
    "llm_platform_chat_requests_total",
    "Total chat requests by mode",
    ["mode"],
)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
