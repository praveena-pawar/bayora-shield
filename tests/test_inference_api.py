from fastapi.testclient import TestClient

from backend.main import app
from security.prompt_detector import DetectionResult, SecurityDecision

client = TestClient(app)


def test_allowed_prompt_reaches_model_gateway(monkeypatch):
    """An ALLOW decision should call the model gateway."""

    gateway_calls = []

    def mock_inspect(prompt: str) -> DetectionResult:
        return DetectionResult(
            decision=SecurityDecision.ALLOW,
            reason="Prompt allowed for testing",
        )

    def mock_inference(prompt: str):
        gateway_calls.append(prompt)
        return type(
            "MockModelResponse",
            (),
            {"response": "Mock inference result"},
        )()

    monkeypatch.setattr(
        "backend.main.inspect_with_blue_team",
        mock_inspect,
    )
    monkeypatch.setattr(
        "backend.main.request_model_inference",
        mock_inference,
    )

    response = client.post(
        "/inference",
        json={"prompt": "Explain machine learning."},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"
    assert response.json()["response"] == "Mock inference result"
    assert gateway_calls == ["Explain machine learning."]


def test_blocked_prompt_never_reaches_model_gateway(monkeypatch):
    """A BLOCK decision must prevent model inference."""

    def mock_inspect(prompt: str) -> DetectionResult:
        return DetectionResult(
            decision=SecurityDecision.BLOCK,
            reason="Blocked for testing",
        )

    def fail_if_called(prompt: str):
        raise AssertionError("Blocked prompt reached the model gateway")

    monkeypatch.setattr(
        "backend.main.inspect_with_blue_team",
        mock_inspect,
    )
    monkeypatch.setattr(
        "backend.main.request_model_inference",
        fail_if_called,
    )

    response = client.post(
        "/inference",
        json={"prompt": "Suspicious test prompt"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"
    assert response.json()["response"] is None


def test_flagged_prompt_never_reaches_model_gateway(monkeypatch):
    """A FLAG decision must prevent model inference."""

    def mock_inspect(prompt: str) -> DetectionResult:
        return DetectionResult(
            decision=SecurityDecision.FLAG,
            reason="Flagged for testing",
        )

    def fail_if_called(prompt: str):
        raise AssertionError("Flagged prompt reached the model gateway")

    monkeypatch.setattr(
        "backend.main.inspect_with_blue_team",
        mock_inspect,
    )
    monkeypatch.setattr(
        "backend.main.request_model_inference",
        fail_if_called,
    )

    response = client.post(
        "/inference",
        json={"prompt": "Prompt requiring review"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "FLAG"
    assert response.json()["response"] is None


def test_blue_team_failure_prevents_model_inference(monkeypatch):
    """A Blue Team failure must prevent inference."""

    from fastapi import HTTPException

    def mock_inspect(prompt: str) -> DetectionResult:
        raise HTTPException(
            status_code=503,
            detail="Blue Team unavailable",
        )

    def fail_if_called(prompt: str):
        raise AssertionError("Model gateway called despite Blue Team failure")

    monkeypatch.setattr(
        "backend.main.inspect_with_blue_team",
        mock_inspect,
    )
    monkeypatch.setattr(
        "backend.main.request_model_inference",
        fail_if_called,
    )

    response = client.post(
        "/inference",
        json={"prompt": "Explain machine learning."},
    )

    assert response.status_code == 503