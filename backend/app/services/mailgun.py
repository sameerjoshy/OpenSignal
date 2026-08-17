"""Mailgun client - email sending + webhook signature verification."""

import hashlib
import hmac
from typing import Any

import httpx

from app.services.base import ServiceError


class MailgunClient:
    def __init__(self, api_key: str, domain: str):
        if not api_key or not domain:
            raise ServiceError("Mailgun API key and domain are required", status_code=400)
        self.api_key = api_key
        self.domain = domain

    async def send(
        self,
        *,
        from_email: str,
        to: str,
        subject: str,
        text: str | None = None,
        html: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        data: dict[str, Any] = {"from": from_email, "to": to, "subject": subject}
        if text:
            data["text"] = text
        if html:
            data["html"] = html
        if tags:
            for tag in tags[:3]:
                data["o:tag"] = tag
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data=data,
            )
        if resp.status_code >= 400:
            raise ServiceError(f"Mailgun send failed ({resp.status_code}): {resp.text[:300]}")
        return resp.json().get("id", "")

    def verify_webhook(self, *, token: str, timestamp: str, signature: str) -> bool:
        """Verify a Mailgun webhook signature (HMAC-SHA256 of timestamp+token with the API key)."""
        if not token or not timestamp or not signature:
            return False
        digest = hmac.new(self.api_key.encode("utf-8"), f"{timestamp}{token}".encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)
