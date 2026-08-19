"""Integration test: campaign create -> import -> detect/score (mocked) -> email generate -> send."""

import asyncio
import uuid

from sqlalchemy import select

from app.database.models import Campaign, CampaignAccount, EmailMessage
from tests.conftest import auth_headers


async def _create_and_import(client, token):
    resp = await client.post(
        "/api/v1/campaigns",
        json={
            "name": "Q3 ABM Sprint",
            "description": "Chrome extension for ops teams",
            "channels": {"email": True, "linkedin": False, "call": False},
            "cadence": {"step_interval_days": 2, "max_steps": 3},
        },
        headers=auth_headers(token),
    )
    campaign = resp.json()
    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/import",
        json={"companies": ["Acme Corp", "Globex Inc"]},
        headers=auth_headers(token),
    )
    return campaign


async def test_full_campaign_flow(client, user_token, db, monkeypatch):
    async def fake_detect(db_, user, account, sources=None):
        from app.database import crud
        from app.database.models import Signal

        await crud.create_signal(
            db_,
            user_id=user.id,
            account_id=account.id,
            source="manual",
            signal_type="funding",
            title=f"Funding signal for {account.company_name}",
        )
        return []

    async def fake_score(db_, user, account):
        account.score = 82
        account.tier = 1
        account.score_rationale = "Test rationale"
        await db_.commit()
        return {"score": 82, "tier": 1, "model_used": "test", "rationale": "test"}

    async def fake_generate(db_, user, account, campaign, *, product_context, sequence_step, template=None, variant="A"):
        return {"subject": f"Re: {account.company_name}", "body": "Personalized body"}

    async def fake_resolve(db_, user, account):
        return "buyer@acme.com"

    monkeypatch.setattr("app.signals.detector.detect_for_account", fake_detect)
    monkeypatch.setattr("app.signals.scorer.score_account", fake_score)
    monkeypatch.setattr("app.email.service.build_personalized_email", fake_generate)
    monkeypatch.setattr("app.email.service.resolve_contact_email", fake_resolve)

    campaign = await _create_and_import(client, user_token)

    resp = await client.post(f"/api/v1/campaigns/{campaign['id']}/run", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["queued"] == 2
    assert "background" in body["message"]

    # The run executes as a background task - poll until the run log confirms completion.
    from app.database.session import AsyncSessionLocal as _Local

    async with _Local() as poll_db:
        for _ in range(50):
            refreshed = await poll_db.get(Campaign, uuid.UUID(campaign["id"]))
            if refreshed and refreshed.run_log and "Processed 2 target(s)" in refreshed.run_log:
                break
            await asyncio.sleep(0.1)

    emails = await client.get(
        f"/api/v1/campaigns/{campaign['id']}/emails", headers=auth_headers(user_token)
    )
    assert len(emails.json()) == 2
    assert all(m["status"] == "draft" for m in emails.json())

    targets = (await db.execute(select(CampaignAccount))).scalars().all()
    assert all(t.status == "ready" for t in targets)
    assert all(t.tier == 1 for t in targets)

    # Analytics reflects the signals
    analytics = await client.get("/api/v1/analytics", headers=auth_headers(user_token))
    assert analytics.status_code == 200
    assert analytics.json()["total_signals"] >= 2
    assert analytics.json()["funnel"][0]["label"] == "Signals detected"


async def test_send_with_mocked_provider(client, user_token, db, monkeypatch):
    campaign = await _create_and_import(client, user_token)

    async def fake_detect(db_, user, account, sources=None):
        from app.database import crud

        await crud.create_signal(
            db_,
            user_id=user.id,
            account_id=account.id,
            source="manual",
            signal_type="news",
            title=f"News about {account.company_name}",
        )
        return []

    async def fake_score(db_, user, account):
        account.score = 55
        account.tier = 2
        await db_.commit()
        return {"score": 55, "tier": 2, "model_used": "test", "rationale": "test"}

    async def fake_generate(db_, user, account, campaign, *, product_context, sequence_step, template=None, variant="A"):
        return {"subject": f"Re: {account.company_name}", "body": "Personalized body"}

    async def fake_resolve(db_, user, account):
        return "buyer@acme.com"

    monkeypatch.setattr("app.signals.detector.detect_for_account", fake_detect)
    monkeypatch.setattr("app.signals.scorer.score_account", fake_score)
    monkeypatch.setattr("app.email.service.build_personalized_email", fake_generate)
    monkeypatch.setattr("app.email.service.resolve_contact_email", fake_resolve)

    await client.post(f"/api/v1/campaigns/{campaign['id']}/run", headers=auth_headers(user_token))

    class FakeMailgun:
        def __init__(self, api_key, domain):
            pass

        async def send(self, **kwargs):
            return "<sent@mailgun.example>"

    monkeypatch.setattr("app.email.service.MailgunClient", FakeMailgun)

    resp = await client.post(
        f"/api/v1/campaigns/{campaign['id']}/send?provider=mailgun", headers=auth_headers(user_token)
    )
    # send requires a stored mailgun key (env empty in tests) -> expect a 400 with clear message
    assert resp.status_code == 400
    assert "Mailgun" in resp.json()["detail"]
