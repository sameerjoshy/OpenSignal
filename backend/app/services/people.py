"""People discovery orchestration - tries Apollo first, falls back to Hunter on the free tier.

Apollo's `mixed_people/search` requires a paid plan. Hunter's Domain Search (50 credits/month
free) is the drop-in alternative for finding decision-makers at a company.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.apollo import ApolloClient
from app.services.base import ServiceError
from app.services.credentials import resolve_credentials
from app.services.hunter import HunterClient
from app.signals.types import SignalDraft

logger = logging.getLogger("opensignal.people")

EXECUTIVE_TITLES = ("ceo", "cto", "cfo", "cmo", "coo", "vp", "vice president", "chief", "director of", "head of")


async def search_people(
    db: AsyncSession,
    user_id,
    company_name: str,
    domain: str | None = None,
    titles: list[str] | None = None,
    *,
    limit: int = 10,
) -> tuple[list[dict], str | None]:
    """Find decision-makers at a company. Returns (people, provider) or ([], None)."""
    apollo_creds = await resolve_credentials(db, user_id, "apollo")
    if apollo_creds and apollo_creds.api_key:
        try:
            client = ApolloClient(apollo_creds.api_key)
            people = await client.search_contacts(company_name, titles, limit=limit)
            if people:
                return people, "apollo"
        except ServiceError as exc:
            logger.info("Apollo people search unavailable (%s); trying Hunter", exc)

    hunter_creds = await resolve_credentials(db, user_id, "hunter")
    if hunter_creds and hunter_creds.api_key and domain:
        try:
            client = HunterClient(hunter_creds.api_key)
            people = await client.search_contacts(domain, titles, limit=limit)
            if people:
                return people, "hunter"
        except ServiceError as exc:
            logger.warning("Hunter people search failed for %s: %s", company_name, exc)

    return [], None


async def people_signals(
    db: AsyncSession,
    user_id,
    company_name: str,
    domain: str | None = None,
) -> list[SignalDraft]:
    """Build key-decision-maker signals from whichever provider is available."""
    people, provider = await search_people(db, user_id, company_name, domain, limit=25)
    signals: list[SignalDraft] = []
    seen: set[str] = set()
    for person in people:
        title = (person.get("title") or "").strip()
        low = title.lower()
        if not any(kw in low for kw in EXECUTIVE_TITLES):
            continue
        name = person.get("name") or person.get("email") or person.get("company_name") or "Contact"
        if name in seen:
            continue
        seen.add(name)
        signals.append(
            SignalDraft(
                source="hunter" if provider == "hunter" else "apollo",
                signal_type="key_decision_maker",
                title=f"{name} - {title} at {company_name}",
                description=f"Identified {title} at {company_name} as a key decision maker.",
                url=person.get("linkedin_url"),
                raw_data={"provider": provider, "email": person.get("email")},
            )
        )
    return signals