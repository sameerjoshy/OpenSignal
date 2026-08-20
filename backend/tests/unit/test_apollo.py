"""Regression tests for Apollo free-plan handling.

Apollo's free plan does not include the `mixed_people/search` endpoint.
The client must surface a clean message instead of a raw error dump, the
connection test must still pass when enrichment works, and signal detection
must not drop enrichment signals when people search is blocked.
"""

import pytest

from app.services.apollo import ApolloClient, _format_error
from app.services.base import ServiceError
from app.services.hunter import HunterClient
from app.services.people import search_people
from tests.conftest import auth_headers

PLAN_BLOCKED_BODY = (
    '{"error":"The api/v1/mixed_people/search API is not included in your Free plan'
    " and is not accessible, even with a master key. All paid plans include full API access."
    ' Upgrade your plan from https://www.apollo.io"}'
)


async def _raise_blocked(*args, **kwargs):
    raise ServiceError(_format_error(403, PLAN_BLOCKED_BODY), status_code=403)


async def _raise_bad_key(*args, **kwargs):
    raise ServiceError(_format_error(401, '{"error":"Unauthorized"}'), status_code=401)


async def _enrich_ok(*args, **kwargs):
    return {}


def test_format_error_plan_restriction_is_clean():
    msg = _format_error(403, PLAN_BLOCKED_BODY)
    assert "mixed_people" not in msg
    assert "raw" not in msg.lower()
    assert "Apollo people search isn't included in your Apollo plan" in msg
    assert "Upgrade at apollo.io" in msg


def test_format_error_other_keeps_status_and_message():
    msg = _format_error(429, '{"error":"Rate limit exceeded"}')
    assert msg.startswith("Apollo request failed (429):")
    assert "Rate limit exceeded" in msg


async def test_apollo_connection_test_passes_on_free_plan(client, user_token, monkeypatch):
    """People search blocked by plan but enrichment works -> connection still connects."""
    monkeypatch.setattr(ApolloClient, "people_search", _raise_blocked)
    monkeypatch.setattr(ApolloClient, "enrich_company", _enrich_ok)

    resp = await client.post(
        "/api/v1/settings/services",
        json={"service": "apollo", "api_key": "apollo-test-key"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["ok"] is True
    assert "paid plan" in body["message"]

    resp = await client.post(
        "/api/v1/settings/services/apollo/test",
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "people search needs an Apollo paid plan" in resp.json()["message"]


async def test_apollo_connection_test_fails_when_enrichment_also_fails(client, user_token, monkeypatch):
    """If enrichment is also unavailable, surface the clean plan-restriction error."""
    monkeypatch.setattr(ApolloClient, "people_search", _raise_blocked)
    monkeypatch.setattr(ApolloClient, "enrich_company", _raise_bad_key)

    resp = await client.post(
        "/api/v1/settings/services",
        json={"service": "apollo", "api_key": "apollo-test-key"},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["ok"] is False
    assert "Apollo people search isn't included in your Apollo plan" in body["message"]


async def test_contacts_search_returns_clean_error(client, user_token, monkeypatch):
    """With the Hunter fallback, a plan-blocked Apollo no longer 403s - it returns gracefully."""
    monkeypatch.setattr(ApolloClient, "search_contacts", _raise_blocked)

    await client.post(
        "/api/v1/settings/services",
        json={"service": "apollo", "api_key": "apollo-test-key"},
        headers=auth_headers(user_token),
    )
    resp = await client.get("/api/v1/contacts/search?company=Stripe", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_people_search_falls_back_to_hunter(db, user_token, monkeypatch):
    """When Apollo people search is plan-blocked, Hunter is used as the free fallback."""
    import uuid

    from app.auth.jwt import decode_access_token
    from app.database import crud
    from app.security.encryption import encrypt_value

    user_id = uuid.UUID(decode_access_token(user_token)["sub"])

    async def _apollo_search(*args, **kwargs):
        raise ServiceError(_format_error(403, PLAN_BLOCKED_BODY), status_code=403)

    async def _hunter_search(*args, **kwargs):
        return [
            {
                "id": "h1",
                "name": "Jordan Lee",
                "first_name": "Jordan",
                "last_name": "Lee",
                "title": "VP Growth",
                "email": "jordan@acme.io",
                "phone": None,
                "company_name": "acme.io",
                "linkedin_url": "https://linkedin.com/in/jordanlee",
            }
        ]

    monkeypatch.setattr(ApolloClient, "search_contacts", _apollo_search)
    monkeypatch.setattr(HunterClient, "search_contacts", _hunter_search)

    await crud.upsert_credential(db, user_id, "apollo", encrypt_value("apollo-key"), None)
    await crud.upsert_credential(db, user_id, "hunter", encrypt_value("hunter-key"), None)

    people, provider = await search_people(db, user_id, "Acme", domain="acme.io", limit=5)
    assert provider == "hunter"
    assert people and people[0]["email"] == "jordan@acme.io"