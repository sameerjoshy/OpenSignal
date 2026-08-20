"""Test/validate a service connection on save (acceptance: credentials tested and validated on save)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.apollo import ApolloClient
from app.services.base import ServiceError
from app.services.deepseek import DeepSeekClient
from app.services.credentials import resolve_credentials, require_key
from app.services.ga4 import Ga4Client
from app.services.hubspot import HubSpotClient
from app.services.hunter import HunterClient
from app.services.mailgun import MailgunClient
from app.services.newsapi import NewsApiClient
from app.services.salesforce import SalesforceClient
from app.services.sec_edgar import SecEdgarClient
from app.services.sendgrid import SendGridClient
from config import settings


async def test_service(db: AsyncSession, user_id, service: str) -> dict:
    creds = await resolve_credentials(db, user_id, service)

    if service == "apollo":
        client = ApolloClient(require_key(creds, "Apollo"))
        try:
            await client.people_search("OpenAI", limit=1)
            return {"ok": True, "message": "Apollo connected", "quota": {"note": "50 searches/month free"}}
        except ServiceError as exc:
            # Free plan doesn't include people search (403). Validate the key a different way
            # so the user can still connect Apollo for company/contact enrichment.
            try:
                await client.enrich_company("openai.com", "OpenAI")
            except ServiceError:
                raise exc
            return {
                "ok": True,
                "message": "Apollo connected (people search needs an Apollo paid plan)",
                "quota": {"note": "People search requires an Apollo paid plan; enrichment works on the free tier"},
            }

    if service == "hunter":
        client = HunterClient(require_key(creds, "Hunter"))
        await client.domain_search("google.com")
        return {"ok": True, "message": "Hunter connected", "quota": {"note": "50 searches/month free"}}

    if service == "mailgun":
        domain = (creds.config or {}).get("domain") or settings.mailgun_domain
        client = MailgunClient(require_key(creds, "Mailgun"), domain)
        await client.send(
            from_email=f"test@{domain}",
            to="test@example.com",
            subject="OpenSignal connection test",
            text="This is a test email from OpenSignal.",
        )
        return {"ok": True, "message": "Mailgun connected (test email sent)", "quota": {"note": "1000 emails/month free"}}

    if service == "sendgrid":
        client = SendGridClient(require_key(creds, "SendGrid"))
        await client.send(
            from_email="test@example.com",
            to="test@example.com",
            subject="OpenSignal connection test",
            text="This is a test email from OpenSignal.",
        )
        return {"ok": True, "message": "SendGrid connected (test email sent)", "quota": {"note": "100 emails/day free"}}

    if service == "hubspot":
        client = HubSpotClient(require_key(creds, "HubSpot"))
        return await client.test_connection()

    if service == "salesforce":
        cfg = creds.config or {}
        client = SalesforceClient(
            require_key(creds, "Salesforce"),
            cfg.get("client_secret") or settings.salesforce_client_secret,
            cfg.get("username") or settings.salesforce_username,
            cfg.get("password") or settings.salesforce_password,
        )
        return await client.test_connection()

    if service == "newsapi":
        client = NewsApiClient(require_key(creds, "NewsAPI"))
        await client.detect_signals("OpenAI", days=1)
        return {"ok": True, "message": "NewsAPI connected", "quota": {"note": "100 requests/day free"}}

    if service == "ga4":
        cfg = creds.config or {}
        client = Ga4Client(
            cfg.get("property_id") or settings.ga4_property_id,
            cfg.get("service_account_json") or settings.ga4_service_account_json,
        )
        await client.detect_signals("Example", days=1)
        return {"ok": True, "message": "GA4 connected", "quota": {"note": "Free tier"}}

    if service == "deepseek":
        client = DeepSeekClient(require_key(creds, "deepseek"))
        await client._chat(
            "Respond with exactly: OK",
            [{"role": "user", "content": "Ping"}],
            max_tokens=8,
            temperature=0,
        )
        return {"ok": True, "message": "DeepSeek connected", "quota": {"note": "Low-cost API"}}

    if service == "sec_edgar":
        client = SecEdgarClient()
        cik = await client.company_cik("Microsoft")
        return {
            "ok": bool(cik),
            "message": "SEC EDGAR connected (public API)" if cik else "SEC EDGAR could not resolve a test company",
            "quota": {"note": "Unlimited, public API"},
        }

    raise ServiceError(f"Unknown service: {service}")
