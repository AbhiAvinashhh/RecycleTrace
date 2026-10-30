"""
RecycleTrace - Authentication & RBAC Tests
"""
import pytest

def test_user_registration_success(client):
    res = client.post("/api/auth/register", json={
        "name": "Jane Citizen",
        "email": "jane@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "user_id" in data
    assert data["role"] == "citizen"

def test_duplicate_email_registration_fails(client):
    payload = {
        "name": "Jane Citizen",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "role": "citizen"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["error"]

def test_invalid_email_format(client):
    res = client.post("/api/auth/register", json={
        "name": "Invalid",
        "email": "not-an-email",
        "password": "Password123!",
        "role": "citizen"
    })
    assert res.status_code == 400
    assert "email" in res.get_json()["details"]

def test_short_password_rejected(client):
    res = client.post("/api/auth/register", json={
        "name": "Short Pass",
        "email": "short@example.com",
        "password": "short",
        "role": "citizen"
    })
    assert res.status_code == 400
    assert "password" in res.get_json()["details"]

def test_login_and_logout(client):
    # Register first
    client.post("/api/auth/register", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "Password123!",
        "role": "citizen"
    })

    # Login
    res = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 200
    assert res.get_json()["user"]["email"] == "login@example.com"

    # Current user
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["email"] == "login@example.com"

    # Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # Current user after logout
    me_res2 = client.get("/api/auth/me")
    assert me_res2.status_code == 401

def test_role_based_access_restriction(client):
    # Register as citizen
    client.post("/api/auth/register", json={
        "name": "Regular Citizen",
        "email": "reg@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    client.post("/api/auth/login", json={
        "email": "reg@example.com",
        "password": "Password123!"
    })

    # Try accessing admin-only endpoint
    admin_res = client.get("/api/admin/users")
    assert admin_res.status_code == 403
    assert "Insufficient permissions" in admin_res.get_json()["error"]

