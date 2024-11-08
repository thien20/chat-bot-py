# test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat():
    response = client.post("/chat", json={"message": "Predict the presidential election 2024!"})
    assert response.status_code == 200
