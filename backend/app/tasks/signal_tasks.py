import asyncio
import uuid

from celery import shared_task

from app.database import crud
from app.database.session import AsyncSessionLocal
from app.signals import detector, scorer


@shared_task(name="signals.detect_account")
def detect_account_task(user_id: str, account_id: str) -> dict:
    """Detect signals for one account (queued via Redis/Upstash)."""

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, uuid.UUID(user_id))
            account = await crud.get_account(db, uuid.UUID(account_id))
            if not user or not account:
                return {"ok": False, "error": "user or account not found"}
            created = await detector.detect_for_account(db, user, account)
            return {"ok": True, "detected": len(created)}

    return asyncio.run(_run())


@shared_task(name="signals.score_account")
def score_account_task(user_id: str, account_id: str) -> dict:
    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, uuid.UUID(user_id))
            account = await crud.get_account(db, uuid.UUID(account_id))
            if not user or not account:
                return {"ok": False, "error": "user or account not found"}
            result = await scorer.score_account(db, user, account)
            return {"ok": True, **result}

    return asyncio.run(_run())
