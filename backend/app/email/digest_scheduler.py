"""Best-effort scheduled weekly digest (no APScheduler dependency).

A background task wakes each day and, on Fridays at the configured hour,
emails the weekly digest to every user that has a mailgun credential saved.
Sends are fire-and-forget and fully guarded - a failure never crashes the API.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.email.digest import send_weekly_digest
from app.services.credentials import resolve_credentials

logger = logging.getLogger("opensignal.digest.scheduler")

DIGEST_HOUR = 9  # 09:00 UTC on Fridays


async def _send_for_user(session_factory, user: User) -> None:
    try:
        async with session_factory() as db:
            creds = await resolve_credentials(db, user.id, "mailgun")
            if not creds or not creds.api_key:
                return
            result = await send_weekly_digest(db, user, provider="mailgun")
            logger.info("Scheduled digest -> %s: %s", user.email, result.get("message"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Scheduled digest failed for %s: %s", user.email, exc)


async def _run_loop(session_factory) -> None:
    now = datetime.utcnow()
    target = time(DIGEST_HOUR, 0, 0)
    next_run = datetime.combine(now.date(), target)
    if now >= next_run:
        next_run += timedelta(days=1)
    while True:
        try:
            await asyncio.sleep(max(0.5, (next_run - datetime.utcnow()).total_seconds()))
        except asyncio.CancelledError:
            return
        if next_run.weekday() == 4:  # Friday
            async with session_factory() as db:
                users = (await db.execute(select(User))).scalars().all()
            for user in users:
                asyncio.create_task(_send_for_user(session_factory, user))
        next_run += timedelta(days=1)


def start_digest_scheduler(session_factory) -> asyncio.Task:
    """Start the background loop. Caller owns the task (cancel on shutdown)."""
    loop = asyncio.get_event_loop()
    return loop.create_task(_run_loop(session_factory))