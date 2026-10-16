from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_dependency_error_returns_evidence_and_recommendation():
    response = client.post("/api/analyze", json={"service":"payments-api","logs":"[ERROR] Could not resolve dependencies for project\nDependency resolution failed"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "findings"
    assert data["service"] == "payments-api"
    finding = next(f for f in data["findings"] if f["rule_id"] == "dependency-resolution")
    assert finding["evidence"] and finding["recommendation"]

def test_unknown_log_is_not_misdiagnosed():
    response = client.post("/api/analyze", json={"logs":"The moon is made of cheese","service":"unknown"})
    assert response.status_code == 200
    assert response.json()["status"] == "unclassified"
    assert response.json()["findings"] == []

def test_empty_logs_are_rejected():
    assert client.post("/api/analyze", json={"logs":""}).status_code == 422

def test_large_log_is_rejected():
    assert client.post("/api/analyze", json={"logs":"x"*200001}).status_code == 422

def test_dashboard_and_rules_are_available():
    assert client.get("/").status_code == 200
    assert len(client.get("/api/rules").json()["rules"]) >= 5

def test_configuration_failure_rule_matches():
    response = client.post("/api/analyze", json={"logs":"Error: environment variable DATABASE_URL not set"})
    assert response.status_code == 200
    assert any(f["rule_id"] == "configuration" for f in response.json()["findings"])


def test_all_failure_categories_are_detected():
    cases = {
        "dependency-resolution": "Could not resolve dependencies",
        "test-failure": "AssertionError: expected true",
        "build-compilation": "Compilation failed",
        "timeout": "Connection refused",
        "configuration": "environment variable DATABASE_URL not set",
        "resource-exhaustion": "Out of memory while building",
    }
    for expected_rule, log_line in cases.items():
        response = client.post("/api/analyze", json={"logs": log_line})
        assert response.status_code == 200, expected_rule
        assert expected_rule in [finding["rule_id"] for finding in response.json()["findings"]], expected_rule


def test_common_secret_values_are_redacted_from_evidence():
    secret = "SuperSecretValue987"
    response = client.post("/api/analyze", json={
        "logs": f"Could not resolve dependencies; password={secret}"
    })
    assert response.status_code == 200
    evidence = "\n".join(
        line for finding in response.json()["findings"] for line in finding["evidence"]
    )
    assert secret not in evidence
    assert "[REDACTED]" in evidence


def test_bearer_tokens_are_redacted_from_evidence():
    token = "eyJhbGciOiJub25lIn0.payload.signature"
    response = client.post("/api/analyze", json={
        "logs": f"Could not resolve dependencies; Authorization: Bearer {token}"
    })
    assert response.status_code == 200
    evidence = "\n".join(
        line for finding in response.json()["findings"] for line in finding["evidence"]
    )
    assert token not in evidence
    assert "[REDACTED]" in evidence


def test_github_tokens_are_redacted_from_evidence():
    token = "ghp_" + "A" * 36
    response = client.post("/api/analyze", json={
        "logs": f"Could not resolve dependencies; token={token}"
    })
    assert response.status_code == 200
    evidence = "\n".join(
        line for finding in response.json()["findings"] for line in finding["evidence"]
    )
    assert token not in evidence
    assert "[REDACTED_GITHUB_TOKEN]" in evidence


def test_blank_service_name_uses_safe_default():
    response = client.post("/api/analyze", json={"service":"   ", "logs":"unknown event"})
    assert response.status_code == 200
    assert response.json()["service"] == "unknown-service"
