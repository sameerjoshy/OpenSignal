"""Signal Detection Engine - pulls buying signals from 5 sources (Apollo, SEC EDGAR, NewsAPI, GA4, Manual)."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, Signal, User
from app.services.apollo import ApolloClient
from app.services.base import ServiceError
from app.services.credentials import require_key, resolve_credentials
from app.services.ga4 import Ga4Client
from app.services.newsapi import NewsApiClient
from app.services.sec_edgar import SecEdgarClient
from app.services.base import ServiceNotConfigured
from app.signals.types import SignalDraft

logger = logging.getLogger("opensignal.signals")

SIGNAL_SOURCES = ["apollo", "sec_edgar", "newsapi", "ga4", "manual"]


async def _detect_source(db: AsyncSession, user_id, account: Account, source: str) -> list[SignalDraft]:
    if source == "apollo":
        creds = await resolve_credentials(db, user_id, "apollo")
        if not creds.api_key:
            return []
        client = ApolloClient(require_key(creds, "Apollo"))
        return await client.detect_signals(account.company_name, account.domain)

    if source == "sec_edgar":
        return await SecEdgarClient().detect_signals(account.company_name)

    if source == "newsapi":
        creds = await resolve_credentials(db, user_id, "newsapi")
        if not creds.api_key:
            return []
        client = NewsApiClient(require_key(creds, "NewsAPI"))
        return await client.detect_signals(account.company_name)

    if source == "ga4":
        creds = await resolve_credentials(db, user_id, "ga4")
        cfg = creds.config or {}
        from config import settings

        property_id = cfg.get("property_id") or settings.ga4_property_id
        sa_json = cfg.get("service_account_json") or settings.ga4_service_account_json
        if not property_id or not sa_json:
            return []
        try:
            client = Ga4Client(property_id, sa_json)
            return await client.detect_signals(account.company_name, account.domain)
        except ServiceNotConfigured:
            return []

    return []


async def detect_for_account(
    db: AsyncSession,
    user: User,
    account: Account,
    sources: list[str] | None = None,
) -> list[Signal]:
    """Detect signals for a single account across configured sources. Graceful per-source degradation."""
    sources = sources or SIGNAL_SOURCES
    existing_titles = await _existing_titles(db, user.id, account.id)

    created: list[Signal] = []
    for source in sources:
        if source == "manual":
            continue
        try:
            drafts = await _detect_source(db, user.id, account, source)
        except ServiceError as exc:
            logger.warning("Signal detection failed for source=%s company=%s: %s", source, account.company_name, exc)
            continue

        for draft in drafts:
            if draft.title in existing_titles:
                continue
            signal = await crud.create_signal(
                db,
                user_id=user.id,
                account_id=account.id,
                source=draft.source,
                signal_type=draft.signal_type,
                title=draft.title,
                description=draft.description,
                url=draft.url,
                raw_data=draft.raw_data,
                detected_at=draft.detected_at,
            )
            created.append(signal)
            existing_titles.add(draft.title)
    return created


async def _existing_titles(db: AsyncSession, user_id, account_id) -> set[str]:
    signals = await crud.list_signals(db, user_id, account_id=account_id, limit=1000)
    return {s.title for s in signals}


async def detect_for_accounts(
    db: AsyncSession,
    user: User,
    accounts: list[Account],
    sources: list[str] | None = None,
) -> dict[str, int]:
    """Detect signals for many accounts; returns {'detected': n, 'errors': n}."""
    detected = 0
    errors = 0
    for account in accounts:
        try:
            created = await detect_for_account(db, user, account, sources)
            detected += len(created)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Detection failed for account %s", account.company_name)
            errors += 1
    return {"detected": detected, "errors": errors}
