from fastapi.testclient import TestClient
from backend.app import app, redact_line

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.2.0"

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

def test_empty_and_whitespace_logs_are_rejected():
    assert client.post("/api/analyze", json={"logs":""}).status_code == 422
    assert client.post("/api/analyze", json={"logs":"   \n  "}).status_code == 422

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

def test_password_and_api_keys_are_redacted_from_evidence():
    secret = "SuperSecretValue987"
    quoted = "private value with spaces"
    response = client.post("/api/analyze", json={
        "logs": f'Could not resolve dependencies; password={secret}; OPENAI_API_KEY="{quoted}"'
    })
    assert response.status_code == 200
    evidence = "\n".join(line for finding in response.json()["findings"] for line in finding["evidence"])
    assert secret not in evidence
    assert quoted not in evidence
    assert "[REDACTED]" in evidence

def test_bearer_tokens_are_redacted_from_evidence():
    token = "eyJhbGciOiJub25lIn0.payload.signature"
    evidence = redact_line(f"Could not resolve dependencies; Authorization: Bearer {token}")
    assert token not in evidence
    assert "[REDACTED]" in evidence

def test_github_tokens_are_redacted_from_evidence():
    token = "ghp_" + "A" * 36
    evidence = redact_line(f"Could not resolve dependencies; token={token}")
    assert token not in evidence
    assert "[REDACTED_GITHUB_TOKEN]" in evidence

def test_aws_access_and_secret_keys_are_redacted():
    access_key = "AKIA1234567890ABCDEF"
    secret = "AWSsecretValue123456"
    evidence = redact_line(f"Could not resolve dependencies; AWS_ACCESS_KEY_ID={access_key}; AWS_SECRET_ACCESS_KEY={secret}")
    assert access_key not in evidence
    assert secret not in evidence
    assert "[REDACTED_AWS_ACCESS_KEY]" in evidence
    assert "[REDACTED]" in evidence

def test_blank_or_oversized_service_name_is_handled():
    response = client.post("/api/analyze", json={"service":"   ", "logs":"unknown event"})
    assert response.status_code == 200
    assert response.json()["service"] == "unknown-service"
    long_name = client.post("/api/analyze", json={"service":"a"*121, "logs":"unknown event"})
    assert long_name.status_code == 422

def test_evidence_lines_are_limited_and_redacted():
    secret = "NeverShowThisToken"
    response = client.post("/api/analyze", json={
        "logs": f"Could not resolve dependencies; password={secret}; " + "x"*900
    })
    evidence = response.json()["findings"][0]["evidence"]
    assert all(len(line) <= 500 for line in evidence)
    assert secret not in "\n".join(evidence)
