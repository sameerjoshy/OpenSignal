"""HubSpot CRM client - create contacts and deals, verify credentials."""

import httpx

from app.services.base import ServiceError

HUBSPOT_BASE = "https://api.hubapi.com"


class HubSpotClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceError("HubSpot API key (private app token) is required", status_code=400)
        self._headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, json: dict | None = None, params: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{HUBSPOT_BASE}{path}", headers=self._headers, json=json, params=params
            )
        if resp.status_code >= 400:
            raise ServiceError(f"HubSpot request failed ({resp.status_code}): {resp.text[:300]}")
        if resp.content:
            return resp.json()
        return {}

    async def test_connection(self) -> dict:
        data = await self._request(
            "POST",
            "/crm/v3/objects/contacts/search",
            json={"limit": 1},
        )
        return {"ok": True, "message": "Connected to HubSpot", "quota": {"total": data.get("total", 0)}}

    async def search_contact(self, email: str) -> str | None:
        data = await self._request(
            "POST",
            "/crm/v3/objects/contacts/search",
            json={"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}]},
        )
        results = data.get("results") or []
        return results[0]["id"] if results else None

    async def create_contact(self, *, email: str, company: str, first_name: str = "", last_name: str = "") -> str:
        existing = await self.search_contact(email)
        if existing:
            return existing
        properties = {"email": email, "company": company}
        if first_name:
            properties["firstname"] = first_name
        if last_name:
            properties["lastname"] = last_name
        data = await self._request("POST", "/crm/v3/objects/contacts", json={"properties": properties})
        return data["id"]

    async def create_deal(self, *, deal_name: str, amount: float | None = None, contact_id: str | None = None) -> str:
        properties = {"dealname": deal_name, "pipeline": "default", "dealstage": "appointmentscheduled"}
        if amount is not None:
            properties["amount"] = str(amount)
        payload: dict = {"properties": properties}
        if contact_id:
            payload["associations"] = [
                {"types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}], "to": {"id": contact_id}}
            ]
        data = await self._request("POST", "/crm/v3/objects/deals", json=payload)
        return data["id"]
