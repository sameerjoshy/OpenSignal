"""Tests for the refinement endpoints: outcomes, learning, replies."""

import uuid

from sqlalchemy import select

from app.database.models import Account, Campaign, EmailReply
from tests.conftest import auth_headers


async def _signup(client) -> tuple[str, str]:
    import random
    import string

    email = f"refine{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "full_name": "Refine User"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    return body["access_token"], body["user"]["id"]


async def _seed_account(client, token):
    resp = await client.post(
        "/api/v1/accounts",
        headers=auth_headers(token),
        json={
            "company_name": "Acme Analytics",
            "domain": "acme.io",
            "industry": "software",
            "employee_count": 120,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_outcomes_endpoint(client, user_token):
    account = await _seed_account(client, user_token)
    # Set a tier + score directly so outcomes have pipeline value.
    resp = await client.post(
        "/api/v1/accounts",
        headers=auth_headers(user_token),
        json={"company_name": "Globex", "domain": "globex.io", "industry": "finance"},
    )
    assert resp.status_code == 201, resp.text

    resp = await client.get("/api/v1/analytics/outcomes", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "pipeline_value" in body
    assert "time_saved_hours" in body
    assert "monthly_forecast" in body
    assert "engagement_lift_pct" in body
    assert body["accounts_scored"] >= 0
    assert body["note"]


async def test_learning_endpoint(client, user_token):
    resp = await client.get("/api/v1/analytics/learning", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"top_attributes", "signal_performance", "email_tactics", "recommendations"}
    assert len(body["recommendations"]) >= 1


async def test_replies_list_endpoint(client, user_token):
    resp = await client.get("/api/v1/replies", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_reply_draft_requires_owned_reply(client):
    token, user_id = await _signup(client)

    # A reply that doesn't exist -> 404
    resp = await client.post(f"/api/v1/replies/{uuid.uuid4()}/draft", headers=auth_headers(token))
    assert resp.status_code == 404

    # Create a classified reply directly to test drafting needs a suggested_reply.
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        from app.database.models import User

        user = (await session.execute(select(User).where(User.id == uuid.UUID(user_id)))).scalar_one()
        reply = EmailReply(
            user_id=user.id,
            from_email="buyer@acme.io",
            subject="Question",
            body="Do you have pricing?",
            classification="question",
            confidence=0.8,
            summary="Wants pricing",
            suggested_reply="Happy to share pricing - are you free Tuesday?",
        )
        session.add(reply)
        await session.commit()
        reply_id = reply.id

    resp = await client.post(f"/api/v1/replies/{reply_id}/draft", headers=auth_headers(token))
    assert resp.status_code == 200
    draft = resp.json()
    assert draft["status"] == "draft"
    assert "pricing" in draft["body_text"].lower()


async def test_replies_scoped_to_user(client):
    token, user_id = await _signup(client)

    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        from app.database.models import User

        user = (await session.execute(select(User).where(User.id == uuid.UUID(user_id)))).scalar_one()
        session.add(
            EmailReply(
                user_id=user.id,
                from_email="buyer@acme.io",
                body="reply",
                classification="hot",
            )
        )
        await session.commit()

    resp = await client.get("/api/v1/replies", headers=auth_headers(token))
    assert resp.status_code == 200
    assert any(r["from_email"] == "buyer@acme.io" for r in resp.json())


async def test_campaign_detail_exposes_run_log(client, user_token):
    resp = await client.post(
        "/api/v1/campaigns",
        headers=auth_headers(user_token),
        json={"name": "Refinement Run Log", "tier_filters": {"tiers": [1, 2]}},
    )
    assert resp.status_code == 201, resp.text
    campaign_id = resp.json()["id"]

    detail = await client.get(f"/api/v1/campaigns/{campaign_id}", headers=auth_headers(user_token))
    assert detail.status_code == 200
    body = detail.json()
    assert "run_log" in body
    assert "last_run_at" in body


async def test_account_intelligence_endpoint(client, user_token):
    account = await _seed_account(client, user_token)
    resp = await client.get(f"/api/v1/accounts/{account['id']}/intelligence", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["account_id"] == account["id"]
    assert "contact_email" in body
    assert "emails_sent" in body
    assert "high_intent_signals" in body
    assert isinstance(body["campaigns"], list)


async def test_campaign_timeline_endpoint(client, user_token):
    resp = await client.post(
        "/api/v1/campaigns",
        headers=auth_headers(user_token),
        json={"name": "Timeline Test"},
    )
    assert resp.status_code == 201, resp.text
    campaign_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/campaigns/{campaign_id}/timeline", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["campaign_id"] == campaign_id
    assert len(body["items"]) >= 1
    assert body["items"][0]["event_type"] == "created"
    assert body["items"][0]["label"] == "Campaign created"


async def test_digest_preview_endpoint(client, user_token):
    resp = await client.get("/api/v1/digest/preview", headers=auth_headers(user_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "subject" in body
    assert "text" in body
    assert "OpenSignal Team" in body["text"]


async def test_digest_send_without_credentials(client, user_token):
    # No mailgun key in tests -> should return a friendly not-configured response.
    resp = await client.post("/api/v1/digest/send", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


async def test_analytics_export_csv(client, user_token):
    resp = await client.get("/api/v1/analytics/export.csv", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    text = resp.text
    assert "metric,value" in text
    assert "pipeline_value" in text