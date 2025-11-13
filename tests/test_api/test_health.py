"""Tests for health check endpoints"""

def test_health_endpoint(client):
    """Test /health endpoint returns 200 and correct structure"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "app_name" in data
    assert "version" in data
    assert "timestamp" in data
    assert "database" in data

    assert data["app_name"] == "XSS Assistant"


def test_root_endpoint(client):
    """Test / root endpoint returns API information"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data

    assert data["message"] == "XSS Assistant API"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
