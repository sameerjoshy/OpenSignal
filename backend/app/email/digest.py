"""Weekly learning digest - a Friday email summarizing what OpenSignal learned."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import service as analytics_service
from app.database import schemas
from app.database.models import EmailMessage, User
from app.email.service import send_message
from app.services.credentials import resolve_credentials

logger = logging.getLogger("opensignal.digest")


async def build_weekly_digest(db: AsyncSession, user: User) -> schemas.DigestPreviewOut:
    analytics = await analytics_service.build_analytics(db, user)
    learning = await analytics_service.build_learning(db, user)
    outcomes = await analytics_service.build_outcomes(db, user)

    rec_lines = "\n".join(f"- {r.label}: {r.detail}" for r in learning.recommendations[:3]) or "- No recommendations yet."

    text = f"""Hi {user.full_name or user.email},

This week, OpenSignal detected {analytics.signals_this_week} signals across {analytics.total_accounts} accounts and you sent {analytics.emails_sent} personalized emails.

YOUR WEEK IN NUMBERS
- Pipeline value: ${outcomes.pipeline_value:,.0f}
- Forecast this month: ${outcomes.monthly_forecast:,.0f} ({outcomes.forecast_growth_pct}% growth)
- Reply rate: {outcomes.reply_rate}% vs {outcomes.industry_reply_rate}% industry
- Open rate: {outcomes.open_rate}%
- Time saved: {outcomes.time_saved_hours}h (${outcomes.labor_value:,.0f} in labor)

WHAT WE LEARNED
{rec_lines}

RECOMMENDED NEXT BEST ACTION
Follow up with any account that clicked but hasn't replied - that's your fastest path to a meeting this week.

Happy selling,
OpenSignal Team
"""
    subject = f"Your Week in Signals: {analytics.signals_this_week} signals · {analytics.emails_sent} sent · {analytics.emails_replied} replies"
    return schemas.DigestPreviewOut(subject=subject, text=text)


async def send_weekly_digest(db: AsyncSession, user: User, provider: str = "mailgun") -> dict:
    creds = await resolve_credentials(db, user.id, provider)
    if not creds or not creds.api_key:
        return {"ok": False, "message": f"Connect {provider} in Settings to email the weekly digest."}
    digest = await build_weekly_digest(db, user)
    message = EmailMessage(
        user_id=user.id,
        subject=digest.subject,
        body_text=digest.text,
        to_email=user.email,
        status="draft",
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    try:
        await send_message(db, user, message, provider=provider)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Weekly digest send failed for %s: %s", user.email, exc)
        return {"ok": False, "message": "Digest could not be sent. Check your email provider setup."}
    logger.info("Weekly digest sent to %s", user.email)
    return {"ok": True, "message": "Weekly digest sent to your inbox."}