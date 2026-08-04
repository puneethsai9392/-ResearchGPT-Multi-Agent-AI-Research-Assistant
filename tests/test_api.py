from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "vector_store_chunks" in data

def test_chat_endpoint():
    response = client.post("/chat", json={"query": "Explain Retrieval-Augmented Generation."})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "final_report" in data
    assert len(data["tasks"]) > 0

def test_sources_endpoint():
    response = client.get("/sources")
    assert response.status_code == 200
    assert "sources" in response.json()

def test_history_and_feedback():
    res = client.get("/history")
    assert res.status_code == 200
    assert "sessions" in res.json()

    fb_res = client.post("/feedback", json={"session_id": "test-session", "rating": 5, "comments": "Great report!"})
    assert fb_res.status_code == 200
