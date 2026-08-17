from tests.conftest import auth_headers


async def _create_account(client, token, name="Acme Corp"):
    resp = await client.post(
        "/api/v1/accounts",
        json={"company_name": name, "domain": "acme.com", "industry": "SaaS"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_and_list_account(client, user_token):
    account = await _create_account(client, user_token)
    resp = await client.get("/api/v1/accounts", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert any(a["id"] == account["id"] for a in resp.json())


async def test_manual_signal_creation(client, user_token):
    account = await _create_account(client, user_token)
    resp = await client.post(
        "/api/v1/signals",
        json={
            "account_id": account["id"],
            "source": "manual",
            "signal_type": "job_change",
            "title": "New VP of Sales hired at Acme Corp",
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201
    assert resp.json()["signal_type"] == "job_change"

    resp = await client.get("/api/v1/signals", headers=auth_headers(user_token))
    assert resp.status_code == 200
    signals = resp.json()
    assert any(s["title"].startswith("New VP of Sales") for s in signals)
    assert signals[0]["account_name"] == "Acme Corp"


async def test_manual_signal_requires_valid_account(client, user_token):
    import uuid

    resp = await client.post(
        "/api/v1/signals",
        json={
            "account_id": str(uuid.uuid4()),
            "source": "manual",
            "signal_type": "news",
            "title": "orphan",
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 404


async def test_detect_without_sources_is_noop(client, user_token, monkeypatch):
    async def no_sources(*args, **kwargs):
        return []

    monkeypatch.setattr("app.signals.detector._detect_source", no_sources)
    account = await _create_account(client, user_token)
    resp = await client.post(
        f"/api/v1/accounts/{account['id']}/detect", headers=auth_headers(user_token)
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_accounts_are_user_scoped(client, user_token):
    await _create_account(client, user_token, name="PrivateCo")
    email = "jennifer@example.com"
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "full_name": "Jennifer Ops"},
    )
    other_token = resp.json()["access_token"]
    resp = await client.get("/api/v1/accounts", headers=auth_headers(other_token))
    assert resp.json() == []
