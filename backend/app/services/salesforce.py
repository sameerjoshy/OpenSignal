"""Salesforce REST client - OAuth 2.0 password flow, create leads."""

import httpx

from app.services.base import ServiceError

LOGIN_URL = "https://login.salesforce.com/services/oauth2/token"
API_VERSION = "v60.0"


class SalesforceClient:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str):
        if not all([client_id, client_secret, username, password]):
            raise ServiceError("Salesforce client id, secret, username and password are required", status_code=400)
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self._access_token: str | None = None
        self._instance_url: str | None = None

    async def _authenticate(self) -> tuple[str, str]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                LOGIN_URL,
                data={
                    "grant_type": "password",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "username": self.username,
                    "password": self.password,
                },
            )
        if resp.status_code >= 400:
            raise ServiceError(f"Salesforce auth failed ({resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        self._access_token = data["access_token"]
        self._instance_url = data.get("instance_url", "")
        return self._access_token, self._instance_url

    async def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        if not self._access_token or not self._instance_url:
            await self._authenticate()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method,
                f"{self._instance_url}{path}",
                headers={"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"},
                json=json,
            )
        if resp.status_code >= 400:
            raise ServiceError(f"Salesforce request failed ({resp.status_code}): {resp.text[:300]}")
        if resp.content:
            return resp.json()
        return {}

    async def test_connection(self) -> dict:
        await self._authenticate()
        return {"ok": True, "message": "Connected to Salesforce", "quota": {}}

    async def create_lead(self, *, company: str, email: str, first_name: str = "", last_name: str = "", description: str = "") -> str:
        payload = {"Company": company, "Email": email, "Status": "New"}
        if first_name:
            payload["FirstName"] = first_name
        if last_name:
            payload["LastName"] = last_name
        if description:
            payload["Description"] = description
        data = await self._request("POST", "/services/data/{0}/sobjects/Lead".format(API_VERSION), json=payload)
        return data.get("id", "")
