"""Regression tests for QA fixes: campaign list counts, accounts tier filter."""

import uuid

from sqlalchemy import select

from app.auth.jwt import decode_access_token
from app.database import crud
from app.database.models import User
from app.database.session import AsyncSessionLocal
from tests.conftest import auth_headers


async def _owner_id(token: str) -> uuid.UUID:
    return uuid.UUID(decode_access_token(token)["sub"])


async def test_campaign_list_returns_counts(client, user_token):
    resp = await client.post(
        "/api/v1/campaigns",
        json={"name": "Counted", "channels": {"email": True}, "cadence": {}},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201
    campaign = resp.json()
    resp = await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp", "Globex Inc"]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200

    resp = await client.get("/api/v1/campaigns", headers=auth_headers(user_token))
    assert resp.status_code == 200
    items = resp.json()
    target = next(c for c in items if c["id"] == campaign["id"])
    assert target["account_count"] == 2
    assert target["sent_count"] == 0
    assert target["reply_count"] == 0


async def test_accounts_tier_filter(client, user_token):
    owner_id = await _owner_id(user_token)
    async with AsyncSessionLocal() as db:
        await crud.find_or_create_account(db, owner_id, "TierOne Co", domain="tierone.com", tier=1)
        await crud.find_or_create_account(db, owner_id, "TierThree Co", domain="tierthree.com", tier=3)

    resp = await client.get("/api/v1/accounts?tier=1", headers=auth_headers(user_token))
    assert resp.status_code == 200
    names = [a["company_name"] for a in resp.json()]
    assert "TierOne Co" in names
    assert "TierThree Co" not in names

    resp = await client.get("/api/v1/accounts?tier=3", headers=auth_headers(user_token))
    names = [a["company_name"] for a in resp.json()]
    assert "TierThree Co" in names
    assert "TierOne Co" not in names