import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_tokenize():
    test_data = {
        "text": "Mhuri yese yakaungana pamba pavakuru.",
        "remove_punctuation": True,
        "remove_stopwords": False
    }
    response = client.post("/api/v1/tokenize", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert "cleaned_text" in data
    assert len(data["tokens"]) > 0

def test_batch_tokenize():
    test_data = {
        "texts": [
            "Mhuri yese yakaungana.",
            "Vana vaitamba panze."
        ],
        "remove_punctuation": True,
        "remove_stopwords": False
    }
    response = client.post("/api/v1/tokenize/batch", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2