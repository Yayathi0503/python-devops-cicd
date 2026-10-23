import os
import pytest
os.environ["DATABASE_URL"] = "sqlite://"
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app import main

# Shared in-memory SQLite database for isolated tests.
main.engine.dispose()
main.engine = main.create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
main.Base.metadata.create_all(main.engine)

@pytest.fixture(autouse=True)
def isolated_students():
    main.Base.metadata.drop_all(main.engine)
    main.Base.metadata.create_all(main.engine)
    yield


def test_liveness_and_readiness():
    with TestClient(main.app) as c:
        assert c.get("/health/live").json() == {"status": "ok"}
        assert c.get("/health/ready").json() == {"status": "ready"}


def test_readiness_fails_when_database_schema_unavailable():
    with TestClient(main.app) as c:
        main.Base.metadata.drop_all(main.engine)
        response = c.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}
        assert c.get("/health/live").status_code == 200


def test_empty_summary():
    with TestClient(main.app) as c:
        assert c.get("/reports/summary").json() == {
            "count": 0, "average_marks": None, "average_attendance": None
        }

def test_health():
    with TestClient(main.app) as c:
        assert c.get("/health").json() == {"status": "ok"}

def test_create_list_update_delete():
    with TestClient(main.app) as c:
        data = {"name":"Demo Student", "attendance":80, "marks":75, "assignment_score":70}
        r = c.post("/students", json=data)
        assert r.status_code == 201
        sid = r.json()["id"]
        assert c.get(f"/students/{sid}").status_code == 200
        assert c.get("/reports/summary").json()["count"] >= 1
        assert c.put(f"/students/{sid}", json={**data,"marks":85}).json()["marks"] == 85
        assert c.delete(f"/students/{sid}").status_code == 204
        assert c.get(f"/students/{sid}").status_code == 404

def test_invalid_input():
    with TestClient(main.app) as c:
        assert c.post("/students", json={"name":"A", "attendance":120,"marks":70,"assignment_score":80}).status_code == 422


def test_missing_student_operations():
    with TestClient(main.app) as c:
        body = {"name": "Demo", "attendance": 80, "marks": 75, "assignment_score": 70}
        assert c.get("/students/999999").status_code == 404
        assert c.put("/students/999999", json=body).status_code == 404
        assert c.delete("/students/999999").status_code == 404


def test_missing_model_returns_service_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.joblib"))
    with TestClient(main.app) as c:
        response = c.post("/predict", json={"attendance": 80, "marks": 75, "assignment_score": 70})
        assert response.status_code == 503


def test_metrics():
    with TestClient(main.app) as c:
        response = c.get("/metrics/")
        assert response.status_code == 200
        assert "python_info" in response.text
