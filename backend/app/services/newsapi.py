import datetime as dt

import httpx

from app.services.base import ServiceError
from app.signals.types import SignalDraft

NEWSAPI_BASE = "https://newsapi.org/v2"

FUNDING_KEYWORDS = ("funding", "raises", "raised", "series a", "series b", "series c", "seed", "valuation", "investment", "m&a", "acquisition", "acquires", "acquired")
LEADERSHIP_KEYWORDS = ("ceo", "cto", "chief", "vp", "hires", "appointed", "appoints", "executive", "board")
PRODUCT_KEYWORDS = ("launch", "launches", "launched", "unveils", "introduces", "product", "release", "beta")


def _classify(title: str) -> str:
    low = title.lower()
    if any(kw in low for kw in FUNDING_KEYWORDS):
        return "funding"
    if any(kw in low for kw in LEADERSHIP_KEYWORDS):
        return "leadership"
    if any(kw in low for kw in PRODUCT_KEYWORDS):
        return "product_launch"
    return "news"


class NewsApiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceError("NewsAPI key is required", status_code=400)
        self.api_key = api_key

    async def detect_signals(self, company_name: str, *, days: int = 30, page_size: int = 20) -> list[SignalDraft]:
        since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
        params = {
            "q": f'"{company_name}"',
            "from": since,
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{NEWSAPI_BASE}/everything", params=params)
        if resp.status_code >= 400:
            raise ServiceError(f"NewsAPI request failed ({resp.status_code}): {resp.text[:300]}")
        articles = (resp.json().get("articles") or [])[:page_size]

        signals: list[SignalDraft] = []
        for article in articles:
            title = article.get("title") or ""
            if not title:
                continue
            signals.append(
                SignalDraft(
                    source="newsapi",
                    signal_type=_classify(title),
                    title=title,
                    description=article.get("description"),
                    url=article.get("url"),
                    raw_data={"article": article},
                )
            )
        return signals
