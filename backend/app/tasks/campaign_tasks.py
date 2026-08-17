import asyncio
import uuid

from celery import shared_task
from sqlalchemy import select

from app.campaigns.service import run_campaign
from app.database import crud
from app.database.models import Campaign
from app.database.session import AsyncSessionLocal


@shared_task(name="campaigns.run")
def run_campaign_task(user_id: str, campaign_id: str) -> dict:
    """Run detection + scoring + email generation for an entire campaign in the background."""

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, uuid.UUID(user_id))
            result = await db.execute(
                select(Campaign).where(
                    Campaign.id == uuid.UUID(campaign_id), Campaign.user_id == user.id
                )
            )
            campaign = result.scalar_one_or_none()
            if not user or not campaign:
                return {"ok": False, "error": "user or campaign not found"}
            outcome = await run_campaign(db, user, campaign)
            return {"ok": True, **outcome}

    return asyncio.run(_run())
