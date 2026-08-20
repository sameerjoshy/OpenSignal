import httpx

from app.services.base import ServiceError

HUNTER_BASE = "https://api.hunter.io/v2"


class HunterClient:
    """Hunter.io client - resolve decision-maker emails from a domain."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceError("Hunter API key is required", status_code=400)
        self.api_key = api_key

    async def email_finder(self, domain: str, full_name: str | None = None) -> dict:
        params = {"api_key": self.api_key, "domain": domain}
        if full_name:
            params["full_name"] = full_name
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{HUNTER_BASE}/email-finder", params=params)
        if resp.status_code >= 400:
            raise ServiceError(f"Hunter request failed ({resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        return data.get("data") or {}

    async def domain_search(self, domain: str) -> dict:
        params = {"api_key": self.api_key, "domain": domain, "limit": 25}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{HUNTER_BASE}/domain-search", params=params)
        if resp.status_code >= 400:
            raise ServiceError(f"Hunter request failed ({resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        return data.get("data") or {}

    async def get_emails(self, domain: str) -> list[str]:
        result = await self.domain_search(domain)
        emails = []
        for item in result.get("emails", [])[:5]:
            if item.get("value"):
                emails.append(item["value"])
        return emails

    async def search_contacts(self, domain: str, titles: list[str] | None = None, *, limit: int = 25) -> list[dict]:
        """Hunter Domain Search - find people (name, title, email) at a company domain.

        This is the free-plan alternative to Apollo's `mixed_people/search`.
        """
        result = await self.domain_search(domain)
        people = []
        for item in result.get("emails", [])[:limit]:
            title = item.get("position") or item.get("seniority") or ""
            if titles and title:
                low = title.lower()
                if not any(kw in low for kw in [t.lower() for t in titles]):
                    continue
            people.append(
                {
                    "id": item.get("id"),
                    "name": f"{item.get('first_name') or ''} {item.get('last_name') or ''}".strip() or None,
                    "first_name": item.get("first_name"),
                    "last_name": item.get("last_name"),
                    "title": title or None,
                    "email": item.get("value"),
                    "phone": None,
                    "company_name": result.get("organization") or None,
                    "linkedin_url": item.get("linkedin"),
                }
            )
        return people
