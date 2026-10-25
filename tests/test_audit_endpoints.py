from fastapi.testclient import TestClient

from backend.main import app, audit_logger

client = TestClient(app)


def test_audit_events_returns_recent_records():
    response = client.get("/audit/events?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] <= 5
    assert isinstance(data["events"], list)

    if data["events"]:
        event = data["events"][0]

        assert "sequence" in event
        assert "event_id" in event
        assert "timestamp" in event
        assert "decision" in event
        assert "reason" in event
        assert "previous_hash" in event
        assert "event_hash" in event


def test_audit_events_rejects_zero_limit():
    response = client.get("/audit/events?limit=0")

    assert response.status_code == 422


def test_audit_events_rejects_limit_above_maximum():
    response = client.get("/audit/events?limit=501")

    assert response.status_code == 422


def test_audit_verify_reports_valid_chain():
    response = client.get("/audit/verify")

    assert response.status_code == 200

    data = response.json()

    assert data["valid"] is True
    assert data["total_events"] == len(audit_logger.events)