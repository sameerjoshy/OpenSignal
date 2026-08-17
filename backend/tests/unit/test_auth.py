from tests.conftest import auth_headers


async def test_signup_returns_token_and_user(client):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "marcus@example.com", "password": "password123", "full_name": "Marcus Growth"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "marcus@example.com"
    assert data["user"]["plan"] == "free"


async def test_signup_duplicate_email_fails(client):
    payload = {"email": "dup@example.com", "password": "password123", "full_name": "Dup"}
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 201
    resp2 = await client.post("/api/v1/auth/signup", json=payload)
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["detail"]


async def test_login_success(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "login@example.com", "password": "password123", "full_name": "Login"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_login_wrong_password_401(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "wrongpw@example.com", "password": "password123", "full_name": "Wrong"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "wrongpw@example.com", "password": "nope"}
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client, user_token):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["email"].startswith("sarah")


async def test_invalid_token_401(client):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers("not-a-real-token"))
    assert resp.status_code == 401
