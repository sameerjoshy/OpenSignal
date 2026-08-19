"""Email generation - DeepSeek personalizes each email per account using detected signals."""

import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, Campaign, User
from app.services.credentials import require_key, resolve_credentials
from app.services.deepseek import DeepSeekClient

logger = logging.getLogger("opensignal.email")


async def build_personalized_email(
    db: AsyncSession,
    user: User,
    account: Account,
    campaign: Campaign,
    *,
    product_context: str,
    sequence_step: int = 1,
    template: dict | None = None,
    variant: str = "A",
) -> dict:
    """Generate {subject, body} via DeepSeek, personalized to the account."""
    signals = await crud.list_signals(
        db, user.id, account_id=account.id, since=datetime.utcnow() - timedelta(days=90), limit=10
    )
    highlights = [{"source": s.source, "signal_type": s.signal_type, "title": s.title} for s in signals]

    sender_name = user.full_name or user.email.split("@")[0]
    account_dict = {
        "company_name": account.company_name,
        "domain": account.domain,
        "industry": account.industry,
        "employee_count": account.employee_count,
    }
    creds = await resolve_credentials(db, user.id, "deepseek")
    deepseek = DeepSeekClient(require_key(creds, "deepseek"))
    return await deepseek.generate_email(
        account=account_dict,
        campaign={"name": campaign.name},
        signal_highlights=highlights,
        sender_name=sender_name,
        sender_title="Founder",
        product_context=product_context,
        sequence_step=sequence_step,
        template=template,
        variant=variant,
    )
