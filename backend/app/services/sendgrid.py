"""SendGrid client - email sending."""

import httpx

from app.services.base import ServiceError


class SendGridClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceError("SendGrid API key is required", status_code=400)
        self.api_key = api_key

    async def send(
        self,
        *,
        from_email: str,
        to: str,
        subject: str,
        text: str | None = None,
        html: str | None = None,
        custom_args: dict | None = None,
    ) -> str:
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to}],
                    "custom_args": custom_args or {},
                }
            ],
            "from": {"email": from_email},
            "subject": subject,
        }
        content: list[dict] = []
        if text:
            content.append({"type": "text/plain", "value": text})
        if html:
            content.append({"type": "text/html", "value": html})
        payload["content"] = content

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
        if resp.status_code >= 400:
            raise ServiceError(f"SendGrid send failed ({resp.status_code}): {resp.text[:300]}")
        return resp.headers.get("X-Message-Id", "")
