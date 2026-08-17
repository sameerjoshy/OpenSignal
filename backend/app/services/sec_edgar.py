"""SEC EDGAR public API - no key required. Requires a descriptive User-Agent."""

import httpx

from app.services.base import ServiceError
from app.signals.types import SignalDraft

USER_AGENT = "OpenSignal (signal-based demand gen; contact: support@opensignal.app)"
BROWSE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
SUBMISSIONS_URL = "https://data.sec.gov/submissions"

# form type -> (signal_type, title prefix)
SIGNAL_FORMS: dict[str, tuple[str, str]] = {
    "S-1": ("funding", "S-1 IPO registration"),
    "S-1/A": ("funding", "S-1 registration amendment"),
    "F-1": ("funding", "F-1 registration"),
    "424B": ("funding", "Prospectus filed"),
    "424B1": ("funding", "Prospectus filed"),
    "424B2": ("funding", "Prospectus filed"),
    "424B4": ("funding", "Prospectus filed"),
    "8-K": ("major_event", "8-K current report"),
    "SC 13D": ("acquisition", "Schedule 13D beneficial ownership"),
    "SC 13G": ("acquisition", "Schedule 13G beneficial ownership"),
    "DEF 14A": ("leadership", "Proxy statement filed"),
    "DEF 14C": ("leadership", "Information statement filed"),
    "10-K": ("earnings", "Annual report (10-K)"),
    "10-Q": ("earnings", "Quarterly report (10-Q)"),
}


class SecEdgarClient:
    """SEC EDGAR client for funding/event signals from regulatory filings."""

    async def _get(self, url: str, params: dict | None = None) -> dict:
        headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers, params=params)
        if resp.status_code >= 400:
            raise ServiceError(f"SEC EDGAR request failed ({resp.status_code})")
        try:
            return resp.json()
        except ValueError as exc:
            raise ServiceError("SEC EDGAR returned an unexpected (non-JSON) response") from exc

    async def company_cik(self, company_name: str) -> str | None:
        data = await self._get(
            BROWSE_URL,
            {
                "action": "getcompany",
                "company": company_name,
                "type": "filings",
                "dateb": "",
                "owner": "include",
                "count": "10",
                "output": "json",
            },
        )
        companies = data.get("companies") or []
        if not companies:
            return None
        return str(companies[0].get("cik_str") or companies[0].get("cik") or "")

    async def recent_filings(self, cik: str, *, days: int = 90) -> list[dict]:
        padded = cik.zfill(10)
        data = await self._get(f"{SUBMISSIONS_URL}/CIK{padded}.json")
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", []) or []
        dates = recent.get("filingDate", []) or []
        accessions = recent.get("accessionNumber", []) or []
        primary_docs = recent.get("primaryDocument", []) or []
        import datetime as dt

        cutoff = dt.date.today() - dt.timedelta(days=days)
        result = []
        for i, form in enumerate(forms):
            try:
                filing_date = dt.date.fromisoformat(dates[i]) if i < len(dates) else dt.date.today()
            except ValueError:
                continue
            if filing_date < cutoff:
                continue
            accession = accessions[i] if i < len(accessions) else ""
            doc = primary_docs[i] if i < len(primary_docs) else ""
            result.append(
                {
                    "form": form,
                    "filing_date": dates[i] if i < len(dates) else "",
                    "accession": accession,
                    "primary_document": doc,
                    "cik": cik,
                }
            )
        return result

    def _filing_url(self, filing: dict) -> str:
        cik = filing.get("cik", "")
        return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={filing.get('form', '')}&dateb=&owner=include&count=40"

    async def detect_signals(self, company_name: str, *, days: int = 90) -> list[SignalDraft]:
        try:
            cik = await self.company_cik(company_name)
        except ServiceError:
            return []
        if not cik:
            return []
        filings = await self.recent_filings(cik, days=days)
        signals: list[SignalDraft] = []
        for filing in filings:
            form = filing.get("form", "")
            mapped = SIGNAL_FORMS.get(form)
            if not mapped:
                continue
            signal_type, prefix = mapped
            acc = filing.get("accession", "").replace("-", "")
            signals.append(
                SignalDraft(
                    source="sec_edgar",
                    signal_type=signal_type,
                    title=f"{prefix} for {company_name}",
                    description=f"{company_name} filed a {form} on {filing.get('filing_date', '')}.",
                    url=f"https://www.sec.gov/Archives/edgar/data/{filing.get('cik', '')}/{acc}/{filing.get('primary_document', '')}"
                    if acc
                    else self._filing_url(filing),
                    raw_data={"filing": filing},
                )
            )
        return signals
