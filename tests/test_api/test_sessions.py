"""Tests for session management endpoints"""

from datetime import datetime, timedelta


def test_create_session_lab_mode(client, db_session, monkeypatch):
    """Test creating session in lab mode (no consent required)"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)
    monkeypatch.setattr(config.settings, "minimal_logging", True)

    # Create target first
    target_response = client.post("/api/v1/targets/", json={
        "name": "Test Target",
        "url": "http://testsite.local"
    })
    target_id = target_response.json()["id"]

    # Create session
    response = client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Test Session",
        "description": "Test session for lab mode"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["target_id"] == target_id
    assert data["name"] == "Test Session"
    assert data["status"] == "pending"


def test_create_session_with_config(client, db_session, monkeypatch):
    """Test creating session with custom configuration"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    # Create session with config
    response = client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Configured Session",
        "config": {
            "timeout": 60,
            "headless": False,
            "screenshots": True
        }
    })

    assert response.status_code == 201
    data = response.json()
    assert data["target_id"] == target_id


def test_create_session_nonexistent_target(client, db_session, monkeypatch):
    """Test creating session for non-existent target"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    response = client.post("/api/v1/sessions/", json={
        "target_id": 99999,
        "name": "Invalid Session"
    })

    assert response.status_code == 404


def test_list_sessions(client, db_session, monkeypatch):
    """Test listing all sessions"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    # Create multiple sessions
    client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Session 1"
    })
    client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Session 2"
    })

    # List sessions
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_list_sessions_with_status_filter(client, db_session, monkeypatch):
    """Test listing sessions with status filter"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target and session
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Pending Session"
    })

    # List pending sessions
    response = client.get("/api/v1/sessions/?status_filter=pending")
    assert response.status_code == 200
    data = response.json()
    assert all(s["status"] == "pending" for s in data)


def test_get_session_by_id(client, db_session, monkeypatch):
    """Test getting specific session by ID"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target and session
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    session_response = client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Test Session"
    })
    session_id = session_response.json()["id"]

    # Get session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["name"] == "Test Session"


def test_get_nonexistent_session(client, db_session):
    """Test getting non-existent session"""
    response = client.get("/api/v1/sessions/99999")
    assert response.status_code == 404


def test_cancel_session(client, db_session, monkeypatch):
    """Test cancelling a running session"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)
    monkeypatch.setattr(config.settings, "minimal_logging", True)

    # Create target and session
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    session_response = client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Session to Cancel"
    })
    session_id = session_response.json()["id"]

    # Cancel session
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 204


def test_approve_session_not_pending(client, db_session, monkeypatch):
    """Test approving a session that's not pending approval"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target and session
    target_response = client.post("/api/v1/targets/", json={
        "name": "Target",
        "url": "http://test.local"
    })
    target_id = target_response.json()["id"]

    session_response = client.post("/api/v1/sessions/", json={
        "target_id": target_id,
        "name": "Session"
    })
    session_id = session_response.json()["id"]

    # Try to approve (should fail since status is 'pending' not 'pending_approval')
    response = client.post(f"/api/v1/sessions/{session_id}/approve", json={
        "approved": True,
        "notes": "Looks good"
    })

    assert response.status_code == 400
    assert "not pending approval" in response.json()["detail"].lower()
