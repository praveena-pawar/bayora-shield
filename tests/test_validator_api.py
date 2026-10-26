from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_validator_api_returns_report():
    response = client.post("/security/validate")

    assert response.status_code == 200

    report = response.json()

    assert report["total_checks"] == 5
    assert report["passed"] == 5
    assert report["failed"] == 0


def test_validator_api_includes_all_check_results():
    response = client.post("/security/validate")

    assert response.status_code == 200

    report = response.json()

    check_names = {
        result["check_name"]
        for result in report["results"]
    }

    assert check_names == {
        "normal_prompt",
        "suspicious_prompt",
        "empty_prompt",
        "audit_integrity",
        "audit_tampering_detection",
    }