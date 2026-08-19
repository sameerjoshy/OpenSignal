from tests.conftest import auth_headers

from app.campaigns.importer import extract_emails, parse_email_file
from app.campaigns.service import extract_email_list


def test_extract_emails_from_text():
    text = "Contact john.doe@acme.com or JANE@Acme.COM, plus support@acme.co.uk today."
    emails = extract_emails(text)
    assert "john.doe@acme.com" in emails
    assert "jane@acme.com" in emails
    assert "support@acme.co.uk" in emails
    assert len(emails) == 3  # dedup + lowercase


def test_extract_email_list_accepts_list_and_text():
    assert extract_email_list(["a@b.com", "A@B.COM", "no email"]) == ["a@b.com"]
    assert extract_email_list("x@y.io, z@w.org") == ["x@y.io", "z@w.org"]
    assert extract_email_list("") == []


def test_parse_email_file_csv_text():
    data = b"Name,Email\nAlice,alice@example.com\nBob,bob@example.com\n"
    assert parse_email_file(data, "list.csv") == ["alice@example.com", "bob@example.com"]
    assert parse_email_file(b"plain@text.com,another@mail.org", "notes.txt") == [
        "plain@text.com",
        "another@mail.org",
    ]


async def _create_campaign(client, token, name="Tier 1 Account-Based"):
    resp = await client.post(
        "/api/v1/campaigns",
        json={
            "name": name,
            "description": "Reach out to companies showing strong buying signals",
            "channels": {"email": True, "linkedin": False, "call": False},
            "cadence": {"step_interval_days": 2, "max_steps": 3},
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_and_list_campaign(client, user_token):
    campaign = await _create_campaign(client, user_token)
    resp = await client.get("/api/v1/campaigns", headers=auth_headers(user_token))
    assert any(c["id"] == campaign["id"] for c in resp.json())


async def test_import_companies_creates_accounts(client, user_token):
    campaign = await _create_campaign(client, user_token)
    resp = await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp", "Globex Inc", "Initech"]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["queued"] == 3

    detail = await client.get(f"/api/v1/campaigns/{campaign['id']}", headers=auth_headers(user_token))
    assert detail.json()["account_count"] == 3

    accounts = await client.get(
        f"/api/v1/campaigns/{campaign['id']}/accounts", headers=auth_headers(user_token)
    )
    assert len(accounts.json()) == 3


async def test_import_deduplicates(client, user_token):
    campaign = await _create_campaign(client, user_token)
    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp"]},
        headers=auth_headers(user_token),
    )
    resp = await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp", "NewCo"]},
        headers=auth_headers(user_token),
    )
    assert resp.json()["queued"] == 1


async def test_status_transitions(client, user_token):
    campaign = await _create_campaign(client, user_token)
    resp = await client.patch(
        f"/api/v1/campaigns/{campaign['id']}",
        json={"status": "active"},
        headers=auth_headers(user_token),
    )
    assert resp.json()["status"] == "active"

    resp = await client.patch(
        f"/api/v1/campaigns/{campaign['id']}",
        json={"status": "draft"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400


async def test_campaign_scoped_to_user(client, user_token):
    campaign = await _create_campaign(client, user_token)
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "other@example.com", "password": "password123", "full_name": "Other"},
    )
    other = resp.json()["access_token"]
    resp = await client.get(f"/api/v1/campaigns/{campaign['id']}", headers=auth_headers(other))
    assert resp.status_code == 404
