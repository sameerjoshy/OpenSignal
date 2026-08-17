"""AI Account Scoring - Bedrock Claude assigns a 0-100 buying-intent score and Tier 1/2/3."""

import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, User
from app.services.bedrock import BedrockClient

logger = logging.getLogger("opensignal.signals")


def _signals_since(days: int = 90) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


async def score_account(db: AsyncSession, user: User, account: Account) -> dict:
    """Score one account and persist score/tier/rationale + a SignalScore log row."""
    signals = await crud.list_signals(db, user.id, account_id=account.id, since=_signals_since(), limit=200)
    signal_dicts = [{"source": s.source, "signal_type": s.signal_type, "title": s.title} for s in signals]

    account_dict = {
        "company_name": account.company_name,
        "domain": account.domain,
        "industry": account.industry,
        "employee_count": account.employee_count,
    }

    bedrock = BedrockClient()  # raises ServiceNotConfigured when AWS keys are absent
    result = await bedrock.score_account(account_dict, signal_dicts)

    account.score = result["score"]
    account.tier = result["tier"]
    account.score_rationale = result.get("rationale")
    await db.commit()
    await db.refresh(account)

    await crud.record_signal_score(
        db,
        user_id=user.id,
        account_id=account.id,
        signal_id=None,
        score=result["score"],
        tier=result["tier"],
        model_used=result.get("model_used"),
        rationale=result.get("rationale"),
    )
    return result


async def score_accounts(db: AsyncSession, user: User, accounts: list[Account]) -> dict:
    scored = 0
    errors = 0
    for account in accounts:
        try:
            await score_account(db, user, account)
            scored += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("Scoring failed for account %s", account.company_name)
            errors += 1
    return {"scored": scored, "errors": errors}
