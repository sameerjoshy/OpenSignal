"""Follow-up engine: surface accounts that engaged but never replied, and send a step-2 nudge."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, Campaign, EmailMessage, User
from app.email.generator import build_personalized_email
from app.email.service import send_message

logger = logging.getLogger("opensignal.followup")


async def list_follow_ups(db: AsyncSession, user: User, limit: int = 20) -> list[dict]:
    """Accounts that clicked but haven't replied - prime follow-up candidates."""
    rows = await db.execute(
        select(EmailMessage, Account.company_name, Campaign.name)
        .outerjoin(Account, Account.id == EmailMessage.account_id)
        .outerjoin(Campaign, Campaign.id == EmailMessage.campaign_id)
        .where(
            EmailMessage.user_id == user.id,
            EmailMessage.clicked_at.isnot(None),
            EmailMessage.replied_at.is_(None),
        )
        .order_by(EmailMessage.clicked_at.desc())
        .limit(limit)
    )
    items = []
    for msg, company, campaign_name in rows.all():
        items.append(
            {
                "message_id": str(msg.id),
                "account_id": str(msg.account_id) if msg.account_id else None,
                "company_name": company,
                "contact_email": msg.to_email,
                "subject": msg.subject,
                "campaign_name": campaign_name,
                "clicked_at": msg.clicked_at.isoformat() if msg.clicked_at else None,
            }
        )
    return items


async def send_follow_up(db: AsyncSession, user: User, message_id) -> dict:
    """Generate + send a step-2 follow-up to a prospect who clicked but didn't reply."""
    message = await db.get(EmailMessage, message_id)
    if not message or message.user_id != user.id:
        raise ValueError("Message not found")
    if message.replied_at:
        raise ValueError("This prospect already replied - no follow-up needed")
    account = await crud.get_account(db, message.account_id) if message.account_id else None
    if not account:
        raise ValueError("Account not found for this message")
    campaign = await db.get(Campaign, message.campaign_id) if message.campaign_id else None
    campaign_name = campaign.name if campaign else "your outreach"

    product_context = campaign.description if campaign else "our B2B product"
    result = await build_personalized_email(
        db,
        user,
        account,
        campaign if campaign else _FakeCampaign(campaign_name),
        product_context=product_context,
        sequence_step=2,
        variant=message.variant,
    )

    follow_up = EmailMessage(
        user_id=user.id,
        campaign_id=message.campaign_id,
        account_id=message.account_id,
        campaign_account_id=message.campaign_account_id,
        subject=f"Re: {message.subject}",
        body_text=result.get("body", ""),
        to_email=message.to_email,
        status="draft",
        sequence_step=2,
        provider=None,
        variant=message.variant,
    )
    db.add(follow_up)
    await db.commit()
    await db.refresh(follow_up)
    await send_message(db, user, follow_up, provider="mailgun")
    logger.info("Follow-up sent to %s (re: %s)", message.to_email, message.subject)
    return {"ok": True, "message": f"Follow-up sent to {message.to_email}", "message_id": str(follow_up.id)}


class _FakeCampaign:
    """Minimal stand-in for campaigns that were deleted but messages remain."""

    def __init__(self, name: str):
        self.name = name
        self.description = None