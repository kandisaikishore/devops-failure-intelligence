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
