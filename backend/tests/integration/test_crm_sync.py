"""Integration test: campaign -> HubSpot CRM sync (mocked)."""

import uuid

import jwt as pyjwt
from sqlalchemy import select

from app.database.models import CampaignAccount, CrmSync
from config import settings
from tests.conftest import auth_headers


def _user_id_from_token(token: str) -> uuid.UUID:
    payload = pyjwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], options={"verify_aud": False}
    )
    return uuid.UUID(payload["sub"])


async def _campaign_with_reply(client, token, db):
    resp = await client.post(
        "/api/v1/campaigns",
        json={"name": "CRM Sync Test", "description": "test"},
        headers=auth_headers(token),
    )
    campaign = resp.json()
    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp"]},
        headers=auth_headers(token),
    )
    target = (
        await db.execute(
            select(CampaignAccount).where(CampaignAccount.campaign_id == uuid.UUID(campaign["id"]))
        )
    ).scalar_one()
    target.status = "replied"
    await db.commit()
    await db.refresh(target)

    # A reply in the inbox marks the account as engaged
    from app.database.models import EmailMessage

    db.add(
        EmailMessage(
            user_id=_user_id_from_token(token),
            campaign_id=uuid.UUID(campaign["id"]),
            account_id=target.account_id,
            subject="Re: quick question",
            body_text="We're interested!",
            to_email="hello@acme.com",
            status="replied",
        )
    )
    await db.commit()
    return campaign


async def test_hubspot_sync_creates_sync_rows(client, user_token, db, monkeypatch):
    campaign = await _campaign_with_reply(client, user_token, db)

    class FakeHubSpot:
        created = []

        def __init__(self, api_key):
            pass

        async def create_contact(self, *, email, company, first_name="", last_name=""):
            self.created.append(("contact", company))
            return "contact_123"

        async def create_deal(self, *, deal_name, amount=None, contact_id=None):
            self.created.append(("deal", deal_name))
            return "deal_123"

    monkeypatch.setattr("app.crm.service.HubSpotClient", FakeHubSpot)

    # No hubspot key in tests -> sync fails gracefully per-account and logs the error
    resp = await client.post(
        "/api/v1/crm/sync",
        json={"campaign_id": campaign["id"], "service": "hubspot"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["errors"] == 1
    error_rows = (await db.execute(select(CrmSync))).scalars().all()
    assert error_rows and error_rows[0].status == "error"
    assert "HubSpot" in (error_rows[0].error_message or "")

    # Now store a credential so the client can be constructed
    from app.database.models import ServiceCredential
    from app.security.encryption import encrypt_value

    db.add(
        ServiceCredential(
            user_id=_user_id_from_token(user_token),
            service="hubspot",
            encrypted_key=encrypt_value("fake-hubspot-token"),
        )
    )
    await db.commit()

    resp = await client.post(
        "/api/v1/crm/sync",
        json={"campaign_id": campaign["id"], "service": "hubspot"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["created"] == 1
    assert FakeHubSpot.created[0] == ("contact", "Acme Corp")
    assert FakeHubSpot.created[1][0] == "deal"

    rows = (await db.execute(select(CrmSync))).scalars().all()
    synced = [r for r in rows if r.status == "synced"]
    assert len(synced) == 1
    assert synced[0].object_type == "opportunity"
    assert synced[0].external_id == "deal_123"
