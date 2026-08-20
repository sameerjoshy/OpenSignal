"""Mock-HTTP tests for service clients with thin coverage (Hunter, SendGrid, HubSpot,
Salesforce, NewsAPI, SEC EDGAR, GA4, Mailgun, DeepSeek, detector fallbacks).

All external HTTP is replaced with fake responses so tests are fast and offline.
"""

import json

import httpx
import pytest

from app.services.base import ServiceError
from app.services.hunter import HunterClient
from app.services.sendgrid import SendGridClient
from app.services.hubspot import HubSpotClient
from app.services.salesforce import SalesforceClient
from app.services.newsapi import NewsApiClient
from app.services.sec_edgar import SecEdgarClient
from app.services.mailgun import MailgunClient
from app.services.deepseek import DeepSeekClient
from app.services.apollo import ApolloClient


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text="", headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {}
        self.content = json.dumps(json_data).encode() if json_data is not None else text.encode()

    def json(self):
        if isinstance(self._json_data, (dict, list)):
            return self._json_data
        return json.loads(self.text)


class FakeClient:
    """Duck-typed httpx.AsyncClient replacement with per-route responses."""

    def __init__(self, responses, headers=None):
        self.responses = responses
        self._headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def _match(self, url):
        for key in ("sendgrid", "hubapi", "salesforce", "newsapi", "mailgun", "hunter", "sec", "ga4", "apollo", "deepseek"):
            if key in url:
                return self.responses[key]
        return self.responses.get("default", FakeResponse(200, {}))

    async def get(self, url, params=None, headers=None, auth=None):
        resp = await self._match(url)
        if isinstance(resp, Exception):
            raise resp
        return resp

    async def post(self, url, params=None, json=None, headers=None, auth=None, data=None):
        resp = await self._match(url)
        if isinstance(resp, Exception):
            raise resp
        return resp

    async def request(self, method, url, json=None, headers=None, params=None):
        resp = await self._match(url)
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.fixture
def monkeypatch_http(monkeypatch):
    holder = {}

    def _patch(responses):
        holder["responses"] = responses
        monkeypatch.setattr(
            "httpx.AsyncClient",
            lambda *a, **k: FakeClient(holder["responses"]),
        )

    return _patch


# ---------------------------------------------------------------- Hunter
async def test_hunter_search_contacts_parses_emails(monkeypatch_http):
    monkeypatch_http(
        {
            "hunter": FakeResponse(
                200,
                {
                    "data": {
                        "organization": "acme.io",
                        "emails": [
                            {"value": "jordan@acme.io", "first_name": "Jordan", "last_name": "Lee",
                             "position": "VP Growth", "linkedin": "https://li/jordan"},
                            {"value": "a@acme.io", "position": "Engineer"},
                        ],
                    }
                },
            )
        }
    )
    client = HunterClient("key")
    people = await client.search_contacts("acme.io", limit=25)
    assert people[0]["email"] == "jordan@acme.io"
    assert people[0]["title"] == "VP Growth"
    assert len(people) == 2


async def test_hunter_search_contacts_filters_by_title(monkeypatch_http):
    monkeypatch_http(
        {
            "hunter": FakeResponse(
                200,
                {
                    "data": {
                        "emails": [
                            {"value": "a@acme.io", "position": "VP Sales"},
                            {"value": "b@acme.io", "position": "Engineer"},
                        ]
                    }
                },
            )
        }
    )
    client = HunterClient("key")
    people = await client.search_contacts("acme.io", titles=["vp"], limit=25)
    assert len(people) == 1
    assert people[0]["email"] == "a@acme.io"


async def test_hunter_error_raises_service_error(monkeypatch_http):
    monkeypatch_http({"hunter": FakeResponse(401, text='{"error":"bad key"}')})
    client = HunterClient("bad")
    with pytest.raises(ServiceError):
        await client.search_contacts("acme.io")


# ---------------------------------------------------------------- SendGrid
async def test_sendgrid_send_success(monkeypatch_http):
    monkeypatch_http({"sendgrid": FakeResponse(202, {}, headers={"X-Message-Id": "msg-1"})})
    client = SendGridClient("key")
    mid = await client.send(from_email="a@x.com", to="b@x.com", subject="Hi", text="hello")
    assert mid == "msg-1"


async def test_sendgrid_send_error(monkeypatch_http):
    monkeypatch_http({"sendgrid": FakeResponse(400, text='{"errors":["bad"]}')})
    client = SendGridClient("key")
    with pytest.raises(ServiceError) as exc:
        await client.send(from_email="a@x.com", to="b@x.com", subject="Hi")
    assert "400" in exc.value.message


# ---------------------------------------------------------------- HubSpot
async def test_hubspot_create_contact_and_deal(monkeypatch_http):
    # search returns no existing -> create contact -> create deal
    monkeypatch_http(
        {
            "hubapi": FakeResponse(
                200,
                {
                    "results": [],
                    "id": "contact-1",
                    "total": 0,
                },
            )
        }
    )
    client = HubSpotClient("key")
    # monkeypatch _request to route by path to keep it simple
    calls = []

    async def fake_request(method, path, json=None, params=None):
        calls.append((method, path, json))
        if "/contacts/search" in path:
            return {"results": []}
        if "/contacts" in path and method == "POST":
            return {"id": "contact-1"}
        if "/deals" in path:
            return {"id": "deal-1"}
        return {}

    client._request = fake_request
    cid = await client.create_contact(email="a@x.com", company="Acme")
    assert cid == "contact-1"
    deal = await client.create_deal(deal_name="Acme", amount=5000, contact_id="contact-1")
    assert deal == "deal-1"


async def test_hubspot_error_raises(monkeypatch_http):
    monkeypatch_http({"hubapi": FakeResponse(401, text='{"message":"unauthorized"}')})
    client = HubSpotClient("key")
    with pytest.raises(ServiceError):
        await client.test_connection()


# ---------------------------------------------------------------- Salesforce
async def test_salesforce_authenticate_and_create_lead(monkeypatch_http):
    client = SalesforceClient("cid", "secret", "u@x.com", "pw")
    called = []

    async def fake_request(method, path, json=None):
        called.append((method, path, json))
        if "oauth2/token" in path:
            client._access_token = "tok"
            client._instance_url = "https://x.salesforce.com"
            return {"access_token": "tok", "instance_url": "https://x.salesforce.com"}
        if "sobjects/Lead" in path:
            return {"id": "00Q000"}
        return {}

    client._request = fake_request
    lead_id = await client.create_lead(company="Acme", email="a@x.com")
    assert lead_id == "00Q000"


async def test_salesforce_auth_error(monkeypatch_http):
    client = SalesforceClient("cid", "secret", "u@x.com", "pw")

    async def fake_request(method, path, json=None):
        if "oauth2/token" in path:
            raise ServiceError("Salesforce auth failed (400): bad")
        return {}

    client._request = fake_request
    with pytest.raises(ServiceError):
        await client._authenticate()


# ---------------------------------------------------------------- NewsAPI
async def test_newsapi_detect_signals_classifies(monkeypatch_http):
    monkeypatch_http(
        {
            "newsapi": FakeResponse(
                200,
                {
                    "articles": [
                        {"title": "Acme raises $40M Series B", "description": "d", "url": "u"},
                        {"title": "Acme launches new product", "url": "u2"},
                    ]
                },
            )
        }
    )
    client = NewsApiClient("key")
    signals = await client.detect_signals("Acme")
    assert signals[0].signal_type == "funding"
    assert signals[1].signal_type == "product_launch"


async def test_newsapi_error(monkeypatch_http):
    monkeypatch_http({"newsapi": FakeResponse(401, text='{"message":"key invalid"}')})
    client = NewsApiClient("bad")
    with pytest.raises(ServiceError):
        await client.detect_signals("Acme")


# ---------------------------------------------------------------- SEC EDGAR
async def test_sec_edgar_detect_signals(monkeypatch_http):
    monkeypatch_http(
        {
            "sec": FakeResponse(
                200,
                {
                    "companies": [{"cik_str": "0000320193"}],
                    "filings": {
                        "recent": {
                            "form": ["8-K", "10-Q", "S-1"],
                            "filingDate": ["2026-08-01", "2026-07-01", "2026-06-01"],
                            "accessionNumber": ["0000000000-26-000001", "x", "y"],
                            "primaryDocument": ["doc1.htm", "doc2.htm", "doc3.htm"],
                        }
                    },
                },
            )
        }
    )
    client = SecEdgarClient()
    signals = await client.detect_signals("Apple", days=120)
    types = {s.signal_type for s in signals}
    assert "major_event" in types  # 8-K
    assert "funding" in types  # S-1
    assert "earnings" in types  # 10-Q


async def test_sec_edgar_graceful_on_missing_cik(monkeypatch_http):
    monkeypatch_http({"sec": FakeResponse(200, {"companies": []})})
    client = SecEdgarClient()
    assert await client.detect_signals("Unknown Co") == []


# ---------------------------------------------------------------- Mailgun
async def test_mailgun_send_success(monkeypatch_http):
    monkeypatch_http({"mailgun": FakeResponse(200, {"id": "msg-1"})})
    client = MailgunClient("key", "mg.example.com")
    mid = await client.send(from_email="a@mg.example.com", to="b@x.com", subject="Hi")
    assert mid == "msg-1"


async def test_mailgun_webhook_verify():
    client = MailgunClient("key", "mg.example.com")
    assert client.verify_webhook(token="t", timestamp="ts", signature="wrong") is False
    # A valid signature computed with the same key (message = timestamp + token)
    import hashlib
    import hmac

    sig = hmac.new(b"key", b"tst", hashlib.sha256).hexdigest()
    assert client.verify_webhook(token="t", timestamp="ts", signature=sig) is True


# ---------------------------------------------------------------- Apollo (company enrichment + signal extraction)
async def test_apollo_detect_signals_enrichment_only_when_people_blocked(monkeypatch_http):
    """People search blocked but enrichment works -> keeps funding signal, no crash."""
    monkeypatch_http(
        {
            "apollo": FakeResponse(
                200,
                {
                    "organization": {
                        "latest_round": "Series B",
                        "total_funding": "$40M",
                        "raw_data": {"latest_round": "Series B"},
                    }
                },
            )
        }
    )
    client = ApolloClient("key")
    # monkeypatch people_search to raise plan-blocked error
    async def blocked(*args, **kwargs):
        raise ServiceError("Apollo people search isn't included in your Apollo plan")

    client.people_search = blocked
    signals = await client.detect_signals("Acme", "acme.com")
    assert any(s.signal_type == "funding" for s in signals)
    assert all(s.signal_type != "key_decision_maker" for s in signals)


async def test_apollo_company_enrichment(monkeypatch_http):
    monkeypatch_http(
        {
            "apollo": FakeResponse(
                200, {"organization": {"latest_round": "Series A", "total_funding": "$10M"}}
            )
        }
    )
    client = ApolloClient("key")
    org = await client.enrich_company("acme.com")
    assert org["latest_round"] == "Series A"


# ---------------------------------------------------------------- DeepSeek (heuristic fallbacks)
async def test_deepseek_score_account_falls_back_on_error(monkeypatch_http):
    monkeypatch_http({"deepseek": httpx.ConnectError("boom")})
    client = DeepSeekClient("key")
    result = await client.score_account(
        {"company_name": "Acme"}, [{"source": "newsapi", "signal_type": "funding", "title": "raised"}]
    )
    assert "model_used" in result
    assert result["model_used"] == "heuristic"


async def test_deepseek_generate_email_falls_back_to_template(monkeypatch_http):
    monkeypatch_http({"deepseek": httpx.ConnectError("boom")})
    client = DeepSeekClient("key")
    result = await client.generate_email(
        account={"company_name": "Acme"},
        campaign={},
        signal_highlights=[],
        sender_name="S",
        sender_title="Rep",
        product_context="our product",
        sequence_step=1,
        template={"subject": "Template subj", "body": "Template body"},
    )
    assert result["model_used"] == "template"
    assert result["subject"] == "Template subj"


