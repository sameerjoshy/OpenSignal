"""Google Analytics 4 Data API client using a service account.

Signals: surge in website sessions for the tracked domain => "website intent".
"""

import asyncio
import datetime as dt
import json
import time

import httpx
import jwt as pyjwt

from app.services.base import ServiceError, ServiceNotConfigured
from app.signals.types import SignalDraft

TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_URL = "https://analyticsdata.googleapis.com/v1beta"

# OAuth tokens are valid for 1h; cache per service account to avoid a token
# request on every report. Keyed by client_email -> (access_token, expires_at).
_token_cache: dict[str, tuple[str, float]] = {}
_token_lock = asyncio.Lock()


class Ga4Client:
    def __init__(self, property_id: str = "", service_account_json: str = ""):
        self.property_id = property_id
        if not property_id or not service_account_json:
            raise ServiceNotConfigured("ga4")
        try:
            self.sa = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise ServiceError("GA4 service account JSON is invalid") from exc
        if not isinstance(self.sa, dict) or not self.sa.get("client_email") or not self.sa.get("private_key"):
            raise ServiceError("GA4 service account JSON must include client_email and private_key")

    async def _access_token(self) -> str:
        cache_key = self.sa.get("client_email", "")
        now = int(time.time())
        cached = _token_cache.get(cache_key)
        if cached and cached[1] > now + 60:
            return cached[0]
        async with _token_lock:
            cached = _token_cache.get(cache_key)
            if cached and cached[1] > now + 60:
                return cached[0]
            assertion = pyjwt.encode(
                {
                    "iss": self.sa["client_email"],
                    "scope": "https://www.googleapis.com/auth/analytics.readonly",
                    "aud": TOKEN_URL,
                    "iat": now,
                    "exp": now + 3600,
                },
                self.sa["private_key"],
                algorithm="RS256",
            )
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    TOKEN_URL,
                    data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                        "assertion": assertion,
                    },
                )
            if resp.status_code >= 400:
                raise ServiceError(f"GA4 token request failed ({resp.status_code}): {resp.text[:300]}")
            token = resp.json()["access_token"]
            _token_cache[cache_key] = (token, now + 3600 - 60)
            return token

    async def _run_report(self, *, start_date: str, end_date: str, domain: str | None = None) -> int:
        token = await self._access_token()
        body = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "metrics": [{"name": "sessions"}],
        }
        if domain:
            body["dimensionFilter"] = {
                "filter": {"fieldName": "hostname", "stringFilter": {"value": domain, "matchType": "CONTAINS"}}
            }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{DATA_URL}/properties/{self.property_id}:runReport",
                headers={"Authorization": f"Bearer {token}"},
                json=body,
            )
        if resp.status_code >= 400:
            raise ServiceError(f"GA4 runReport failed ({resp.status_code}): {resp.text[:300]}")
        rows = resp.json().get("rows") or []
        if not rows:
            return 0
        return int(rows[0].get("metricValues", [{}])[0].get("value", 0))

    async def detect_signals(self, company_name: str, domain: str | None = None, *, days: int = 14) -> list[SignalDraft]:
        today = dt.date.today()
        current = await self._run_report(
            start_date=(today - dt.timedelta(days=7)).isoformat(),
            end_date=today.isoformat(),
            domain=domain,
        )
        previous = await self._run_report(
            start_date=(today - dt.timedelta(days=14)).isoformat(),
            end_date=(today - dt.timedelta(days=7)).isoformat(),
            domain=domain,
        )
        if current < 5 or previous <= 0:
            return []
        growth = (current - previous) / previous * 100
        if growth < 30:
            return []
        return [
            SignalDraft(
                source="ga4",
                signal_type="website_intent",
                title=f"Website intent surge: {growth:.0f}% session growth for {company_name}",
                description=f"Website sessions grew {growth:.0f}% week over week ({previous} -> {current}).",
                raw_data={"current_sessions": current, "previous_sessions": previous, "growth_pct": growth},
            )
        ]
