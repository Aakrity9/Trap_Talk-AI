import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import init_db

# Initialize database tables for testing
init_db()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_engage_auth_failure():
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Hello, pay now",
            "timestamp": 123456789
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS"
        }
    }
    response = client.post("/api/v1/engage", json=payload)
    assert response.status_code == 401

def test_engage_invalid_auth_key():
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Hello, pay now",
            "timestamp": 123456789
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS"
        }
    }
    response = client.post(
        "/api/v1/engage",
        json=payload,
        headers={"x-api-key": "wrong_key"}
    )
    assert response.status_code == 403

def test_engage_success_and_lifecycle():
    session_id = "test-session-lifecycle"
    
    # 1. Engage with first message (Scam attempt)
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Alert: Your bank account is blocked. Verify immediately at http://scam.link. UPI ID scammer@pay",
            "timestamp": 1770005528000
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS"
        }
    }
    
    response = client.post(
        "/api/v1/engage",
        json=payload,
        headers={"x-api-key": settings.API_KEY}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert "reply" in res_data
    
    # 2. Get report of the session
    report_response = client.get(
        f"/api/v1/sessions/{session_id}/report",
        headers={"x-api-key": settings.API_KEY}
    )
    assert report_response.status_code == 200
    report_data = report_response.json()
    assert report_data["sessionId"] == session_id
    assert report_data["scamDetected"] is True
    assert "scammer@pay" in report_data["extractedIntelligence"]["upiIds"]
    assert "http://scam.link" in report_data["extractedIntelligence"]["phishingLinks"]
    assert report_data["totalMessagesExchanged"] >= 1

    # 3. Close the session
    close_response = client.post(
        f"/api/v1/sessions/{session_id}/close",
        headers={"x-api-key": settings.API_KEY}
    )
    assert close_response.status_code == 200
    close_data = close_response.json()
    assert close_data["sessionId"] == session_id
    assert close_data["scamDetected"] is True
