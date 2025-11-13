"""Tests for target management endpoints"""

from datetime import datetime, timedelta


def test_create_target_without_consent_lab_mode(client, db_session, monkeypatch):
    """Test creating target without consent in lab mode"""
    # Mock settings to disable consent requirement
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)
    monkeypatch.setattr(config.settings, "minimal_logging", True)

    response = client.post("/api/v1/targets/", json={
        "name": "Test Target",
        "url": "http://testsite.local",
        "description": "Test target for lab mode"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Target"
    assert data["url"] == "http://testsite.local/"
    assert data["is_authorized"] == True


def test_create_target_with_consent(client, db_session):
    """Test creating target with valid consent"""
    consent_data = {
        "authorized_by": "John Doe",
        "authorization_email": "john@example.com",
        "authorization_date": datetime.utcnow().isoformat(),
        "expiry_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "scope": ["xss_testing", "dom_analysis"],
        "signature": "test_signature_base64",
        "signature_algorithm": "SHA256-RSA"
    }

    response = client.post("/api/v1/targets/", json={
        "name": "Authorized Target",
        "url": "https://example.com",
        "description": "Target with consent",
        "consent": consent_data
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Authorized Target"
    assert data["is_authorized"] == True


def test_create_target_without_consent_production_mode(client, db_session, monkeypatch):
    """Test creating target without consent in production mode (should fail)"""
    # Ensure production mode
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", True)

    response = client.post("/api/v1/targets/", json={
        "name": "Test Target",
        "url": "http://testsite.local",
        "description": "Test target without consent"
    })

    assert response.status_code == 400
    assert "Consent required" in response.json()["detail"]


def test_create_target_with_expired_consent(client, db_session):
    """Test creating target with expired consent"""
    expired_consent = {
        "authorized_by": "John Doe",
        "authorization_email": "john@example.com",
        "authorization_date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
        "expiry_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "scope": ["xss_testing"],
        "signature": "test_signature",
        "signature_algorithm": "SHA256-RSA"
    }

    response = client.post("/api/v1/targets/", json={
        "name": "Expired Target",
        "url": "https://example.com",
        "consent": expired_consent
    })

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_list_targets(client, db_session, monkeypatch):
    """Test listing all targets"""
    # Create a target first (in lab mode)
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)
    monkeypatch.setattr(config.settings, "minimal_logging", True)

    client.post("/api/v1/targets/", json={
        "name": "Target 1",
        "url": "http://test1.local"
    })

    client.post("/api/v1/targets/", json={
        "name": "Target 2",
        "url": "http://test2.local"
    })

    # List targets
    response = client.get("/api/v1/targets/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_target_by_id(client, db_session, monkeypatch):
    """Test getting specific target by ID"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target
    create_response = client.post("/api/v1/targets/", json={
        "name": "Test Target",
        "url": "http://testsite.local"
    })
    target_id = create_response.json()["id"]

    # Get target
    response = client.get(f"/api/v1/targets/{target_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_id
    assert data["name"] == "Test Target"


def test_get_nonexistent_target(client, db_session):
    """Test getting non-existent target"""
    response = client.get("/api/v1/targets/99999")
    assert response.status_code == 404


def test_delete_target(client, db_session, monkeypatch):
    """Test soft-deleting a target"""
    from backend.app import config
    monkeypatch.setattr(config.settings, "require_consent", False)

    # Create target
    create_response = client.post("/api/v1/targets/", json={
        "name": "Target to Delete",
        "url": "http://delete.local"
    })
    target_id = create_response.json()["id"]

    # Delete target
    response = client.delete(f"/api/v1/targets/{target_id}")
    assert response.status_code == 204

    # Verify target is inactive (soft deleted)
    # Note: This won't appear in list_targets since we filter is_active=True
