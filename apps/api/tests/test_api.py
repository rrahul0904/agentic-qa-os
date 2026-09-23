from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_registry_has_ready_generator():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert any(a["id"] == "test-case-generator" and a["status"] == "ready" for a in agents)


def test_agent_registry_has_ready_temporal_designer():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert any(a["id"] == "temporal-test-designer" and a["status"] == "ready" for a in agents)


def test_test_case_generator_returns_evidence_linked_cases():
    response = client.post("/api/v1/agents/test-case-generator/run", json={"requirement": "Customer must receive an email receipt after a successful payment.", "source_id": "JIRA-428"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert len(body["test_cases"]) == 3
    assert {c["kind"] for c in body["test_cases"]} == {"positive", "negative", "boundary"}
    assert all(c["evidence"][0]["source_id"] == "JIRA-428" for c in body["test_cases"])


def test_temporal_designer_returns_time_boundary_plan_without_execution_claims():
    response = client.post(
        "/api/v1/agents/temporal-test-designer/run",
        json={
            "requirement": "A subscription should renew exactly once at the end of its billing period.",
            "source_id": "REQ-TIME-17",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == "temporal-test-designer"
    assert body["status"] == "completed"
    assert len(body["test_cases"]) == 6
    assert {"TIME-YEAR-001", "TIME-ROLLBACK-005", "TIME-RATE-006"} <= {case["id"] for case in body["test_cases"]}
    assert all(case["evidence"][0]["source_id"] == "REQ-TIME-17" for case in body["test_cases"])
    assert any("does not yet alter" in warning for warning in body["warnings"])


def test_planned_agent_is_not_fake_executable():
    response = client.post("/api/v1/agents/release-readiness/run", json={"requirement": "Release must be safe"})
    assert response.status_code == 409
