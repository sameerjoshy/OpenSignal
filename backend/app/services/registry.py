"""Metadata for every integratable service (free/paid tiers per PRD)."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServiceMeta:
    id: str
    name: str
    description: str
    env_api_key: str
    requires_config: bool = False
    free_tier_note: str = ""
    tags: list[str] = field(default_factory=list)


SERVICES: list[ServiceMeta] = [
    ServiceMeta(
        "apollo",
        "Apollo",
        "Company & people search. Detect job changes, hiring sprees and funding signals.",
        "apollo_api_key",
        free_tier_note="50 searches/month free",
        tags=["signal"],
    ),
    ServiceMeta(
        "hunter",
        "Hunter",
        "Email finder. Resolve decision-maker email addresses from a domain.",
        "hunter_api_key",
        free_tier_note="50 searches/month free",
        tags=["email"],
    ),
    ServiceMeta(
        "mailgun",
        "Mailgun",
        "Transactional email delivery with open/click tracking and webhooks.",
        "mailgun_api_key",
        requires_config=True,
        free_tier_note="1000 emails/month free",
        tags=["email"],
    ),
    ServiceMeta(
        "sendgrid",
        "SendGrid",
        "Transactional email delivery via Twilio SendGrid.",
        "sendgrid_api_key",
        free_tier_note="100 emails/day free",
        tags=["email"],
    ),
    ServiceMeta(
        "hubspot",
        "HubSpot",
        "CRM sync. Create contacts and deals automatically.",
        "hubspot_api_key",
        free_tier_note="Free CRM plan",
        tags=["crm"],
    ),
    ServiceMeta(
        "salesforce",
        "Salesforce",
        "CRM sync. Create leads and opportunities.",
        "salesforce_client_id",
        requires_config=True,
        free_tier_note="Developer edition free",
        tags=["crm"],
    ),
    ServiceMeta(
        "newsapi",
        "NewsAPI",
        "News & press signals (funding, launches, leadership changes).",
        "newsapi_key",
        free_tier_note="100 requests/day free",
        tags=["signal"],
    ),
    ServiceMeta(
        "ga4",
        "Google Analytics 4",
        "Website intent signals from your GA4 property.",
        "ga4_property_id",
        requires_config=True,
        free_tier_note="Free",
        tags=["signal"],
    ),
    ServiceMeta(
        "sec_edgar",
        "SEC EDGAR",
        "Regulatory filings (8-K, S-1, 13D) - funding & event signals.",
        "",
        free_tier_note="Public API, unlimited",
        tags=["signal"],
    ),
    ServiceMeta(
        "bedrock",
        "AWS Bedrock",
        "Claude scoring and personalized email generation.",
        "aws_access_key_id",
        free_tier_note="Free credits ($100/month value)",
        tags=["ai"],
    ),
]

SERVICE_IDS = [s.id for s in SERVICES]
SERVICE_BY_ID = {s.id: s for s in SERVICES}
