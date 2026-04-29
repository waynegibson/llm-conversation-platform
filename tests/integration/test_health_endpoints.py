from api.deps import get_db_session, get_ollama_service
from fastapi.testclient import TestClient
from main import app


class _DbStub:
    def execute(self, *_args, **_kwargs):
        return None


class _OllamaUp:
    def is_available(self) -> bool:
        return True


class _OllamaDown:
    def is_available(self) -> bool:
        return False


def _db_override():
    yield _DbStub()


def test_health_ready_and_metrics_success() -> None:
    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_ollama_service] = lambda: _OllamaUp()

    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "llm_platform_http_requests_total" in metrics.text

    app.dependency_overrides.clear()


def test_health_returns_503_when_ollama_unavailable() -> None:
    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_ollama_service] = lambda: _OllamaDown()

    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 503
    assert "error" in response.json()

    app.dependency_overrides.clear()
