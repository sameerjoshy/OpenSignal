import json
import logging

import httpx

from app.services.base import ServiceError
from app.signals.types import SignalDraft

logger = logging.getLogger("opensignal.apollo")

APOLLO_BASE = "https://api.apollo.io/api/v1"

EXECUTIVE_TITLES = ("ceo", "cto", "cfo", "cmo", "coo", "vp", "vice president", "chief", "director of", "head of")

_PLAN_RESTRICTION_MARKERS = (
    "not included in your Free plan",
    "not accessible, even with a master key",
    "is not included in your plan",
    "upgrade your plan",
)


def _format_error(status: int, body_text: str) -> str:
    """Build a user-friendly error for Apollo failures (raw bodies are noisy JSON)."""
    msg = body_text[:300]
    try:
        data = json.loads(body_text)
        msg = data.get("error") or data.get("message") or data.get("detail") or msg
    except (ValueError, TypeError):
        pass

    lowered = f"{body_text} {msg}".lower()
    if status == 403 or any(marker in lowered for marker in _PLAN_RESTRICTION_MARKERS):
        return (
            "Apollo people search isn't included in your Apollo plan. "
            "Upgrade at apollo.io, or remove Apollo from this flow and it won't block the rest."
        )
    return f"Apollo request failed ({status}): {msg}"


class ApolloClient:
    """Apollo API client (companies/people enrichment + signal extraction)."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceError("Apollo API key is required", status_code=400)
        self._headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    async def _post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{APOLLO_BASE}{path}", headers=self._headers, json=payload)
        if resp.status_code >= 400:
            raise ServiceError(_format_error(resp.status_code, resp.text), status_code=resp.status_code)
        return resp.json()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{APOLLO_BASE}{path}", headers=self._headers, params=params or {})
        if resp.status_code >= 400:
            raise ServiceError(_format_error(resp.status_code, resp.text), status_code=resp.status_code)
        return resp.json()

    async def enrich_company(self, domain: str | None, company_name: str | None = None) -> dict:
        payload = {}
        if domain:
            payload["domain"] = domain
        elif company_name:
            payload["organization_name"] = company_name
        if not payload:
            return {}
        data = await self._post("/organizations/enrich", payload)
        return data.get("organization") or {}

    async def people_search(self, company_name: str, *, limit: int = 10) -> list[dict]:
        data = await self._post(
            "/mixed_people/search",
            {"q_keywords": company_name, "person_titles": list(EXECUTIVE_TITLES[:4]), "limit": limit},
        )
        return data.get("people") or []

    async def search_contacts(self, company_name: str, titles: list[str] | None = None, *, limit: int = 10) -> list[dict]:
        """Apollo People Search - find decision-makers at a company."""
        payload: dict = {"q_keywords": company_name, "limit": limit}
        if titles:
            payload["person_titles"] = titles[:4]
        else:
            payload["person_titles"] = list(EXECUTIVE_TITLES[:4])
        data = await self._post("/mixed_people/search", payload)
        people = data.get("people") or []
        return [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "first_name": p.get("first_name"),
                "last_name": p.get("last_name"),
                "title": p.get("title"),
                "email": p.get("email"),
                "phone": p.get("phone"),
                "company_name": p.get("organization_name"),
                "linkedin_url": p.get("linkedin_url"),
            }
            for p in people
        ]

    async def enrich_contact(self, email: str) -> dict:
        """Apollo Enrichment - resolve a contact's role + company details from an email."""
        data = await self._post(
            "/people/match",
            {"email": email, "reveal_personal_emails": False, "reveal_phone_number": False},
        )
        person = data.get("person") or {}
        return {
            "name": person.get("name"),
            "title": person.get("title"),
            "phone": person.get("phone"),
            "company_name": person.get("organization_name"),
            "company_size": (person.get("organization") or {}).get("estimated_num_employees"),
            "raised": (person.get("organization") or {}).get("raw_data", {}).get("latest_round"),
            "industry": (person.get("organization") or {}).get("industry"),
            "linkedin_url": person.get("linkedin_url"),
        }

    async def detect_signals(self, company_name: str, domain: str | None) -> list[SignalDraft]:
        signals: list[SignalDraft] = []
        org = await self.enrich_company(domain, company_name)

        funding = org.get("raw_data") or {}
        latest_round = org.get("latest_round") or funding.get("latest_round")
        total_funding = org.get("total_funding") or funding.get("total_funding")
        if latest_round or total_funding:
            signals.append(
                SignalDraft(
                    source="apollo",
                    signal_type="funding",
                    title=f"{company_name} raised {total_funding or latest_round or 'a new round'}",
                    description=f"Latest round: {latest_round}. Total funding: {total_funding}.",
                    raw_data={"latest_round": latest_round, "total_funding": total_funding},
                )
            )

        people = []
        try:
            people = await self.people_search(company_name)
        except ServiceError as exc:
            # People search is a paid-plan endpoint; don't drop enrichment signals because of it.
            logger.warning("Apollo people search unavailable for %s: %s", company_name, exc)
        for person in people[:10]:
            title = person.get("title") or ""
            low = title.lower()
            if any(kw in low for kw in EXECUTIVE_TITLES):
                name = person.get("name") or person.get("first_name", "") + " " + person.get("last_name", "")
                signals.append(
                    SignalDraft(
                        source="apollo",
                        signal_type="key_decision_maker",
                        title=f"{name} - {title} at {company_name}",
                        description=f"Identified {title} at {company_name} as a key decision maker.",
                        url=person.get("linkedin_url"),
                        raw_data={"person": person},
                    )
                )
        return signals
