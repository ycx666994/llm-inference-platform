import json

import pytest
from fastapi.testclient import TestClient

from app import main as gateway_main
from app.rate_limit import InMemoryRateLimiter


class DummyUpstreamResponse:
    status_code = 200
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "hello"},
                    "finish_reason": "stop",
                }
            ],
        }
    ).encode("utf-8")


class DummyAsyncClient:
    last_url = None
    last_payload = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, json):
        self.__class__.last_url = url
        self.__class__.last_payload = json
        return DummyUpstreamResponse()


@pytest.fixture(autouse=True)
def reset_gateway_state(monkeypatch):
    gateway_main.limiter = InMemoryRateLimiter(max_requests=60)
    monkeypatch.setattr(gateway_main.httpx, "AsyncClient", DummyAsyncClient)
    DummyAsyncClient.last_url = None
    DummyAsyncClient.last_payload = None
    yield
    gateway_main.limiter = InMemoryRateLimiter(max_requests=60)


@pytest.fixture
def client():
    return TestClient(gateway_main.app)


def test_healthz(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_completions_requires_bearer_token(client):
    response = client.post("/v1/chat/completions", json={"messages": []})

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_chat_completions_rejects_invalid_api_key(client):
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer invalid"},
        json={"messages": []},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key"


def test_chat_completions_forwards_to_upstream_with_default_model(client):
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer sk-demo"},
        json={"messages": [{"role": "user", "content": "hello"}]},
    )

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hello"
    assert DummyAsyncClient.last_url == "http://localhost:8000/v1/chat/completions"
    assert DummyAsyncClient.last_payload["model"] == "Qwen/Qwen2.5-0.5B-Instruct"


def test_chat_completions_rate_limits_per_api_key(client):
    gateway_main.limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)

    first = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer sk-demo"},
        json={"messages": []},
    )
    second = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer sk-demo"},
        json={"messages": []},
    )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"] == "Rate limit exceeded"


def test_metrics_endpoint_exposes_gateway_metrics(client):
    client.get("/healthz")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "gateway_requests_total" in response.text
    assert "gateway_request_latency_seconds" in response.text
