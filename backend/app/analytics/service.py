"""Analytics - real-time metrics, conversion funnel, weekly activity."""

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud, schemas
from app.database.models import Account, Campaign, EmailEvent, EmailMessage, Signal, User


async def build_analytics(db: AsyncSession, user: User) -> schemas.AnalyticsOut:
    week_ago = dt.datetime.utcnow() - dt.timedelta(days=7)

    total_signals = await crud.count(db, Signal, user_id=user.id)
    total_accounts = await crud.count(db, Account, user_id=user.id)
    total_campaigns = await crud.count(db, Campaign, user_id=user.id)
    active_campaigns = await crud.count(db, Campaign, user_id=user.id, status="active")
    signals_this_week = await crud.count_signals_since(db, user.id, week_ago)

    # Email metrics by message status
    emails_sent = await crud.count(db, EmailMessage, user_id=user.id, status="sent")
    emails_opened = await crud.count(db, EmailMessage, user_id=user.id, status="opened")
    emails_clicked = await crud.count(db, EmailMessage, user_id=user.id, status="clicked")
    emails_replied = await crud.count(db, EmailMessage, user_id=user.id, status="replied")
    emails_delivered = await crud.count(db, EmailMessage, user_id=user.id, status="delivered")

    # Include statuses that imply opens/clicks/replies even if status moved on
    for extra_status in ("clicked", "replied"):
        pass

    # Top signal sources
    source_rows = await db.execute(
        select(Signal.source, func.count(Signal.id))
        .where(Signal.user_id == user.id)
        .group_by(Signal.source)
        .order_by(func.count(Signal.id).desc())
        .limit(5)
    )
    top_sources = [schemas.MetricPoint(label=row[0], value=row[1]) for row in source_rows.all()]

    # Signals by tier
    tier_rows = await db.execute(
        select(Account.tier, func.count(Signal.id))
        .join(Signal, Signal.account_id == Account.id)
        .where(Signal.user_id == user.id)
        .group_by(Account.tier)
    )
    signals_by_tier = []
    for row in tier_rows.all():
        label = {1: "Tier 1", 2: "Tier 2", 3: "Tier 3"}.get(row[0], "Unscored")
        signals_by_tier.append(schemas.MetricPoint(label=label, value=row[1]))

    # Conversion funnel
    funnel = [
        schemas.FunnelStep(label="Signals detected", value=total_signals),
        schemas.FunnelStep(label="Accounts scored", value=total_accounts),
        schemas.FunnelStep(label="Emails sent", value=emails_sent),
        schemas.FunnelStep(label="Opened", value=emails_opened),
        schemas.FunnelStep(label="Clicked", value=emails_clicked),
        schemas.FunnelStep(label="Replied", value=emails_replied),
    ]

    # Weekly activity (signals per day, last 7 days)
    since = dt.datetime.utcnow() - dt.timedelta(days=6)
    since = since.replace(hour=0, minute=0, second=0, microsecond=0)
    day_rows = await db.execute(
        select(func.date(Signal.detected_at), func.count(Signal.id))
        .where(Signal.user_id == user.id, Signal.detected_at >= since)
        .group_by(func.date(Signal.detected_at))
    )
    counts_by_day = {str(row[0]): row[1] for row in day_rows.all()}
    weekly_activity = []
    for i in range(7):
        day = (since + dt.timedelta(days=i)).date()
        weekly_activity.append(schemas.MetricPoint(label=day.strftime("%a"), value=counts_by_day.get(str(day), 0)))

    return schemas.AnalyticsOut(
        total_signals=total_signals,
        total_accounts=total_accounts,
        total_campaigns=total_campaigns,
        emails_sent=emails_sent,
        emails_opened=emails_opened,
        emails_clicked=emails_clicked,
        emails_replied=emails_replied,
        active_campaigns=active_campaigns,
        signals_this_week=signals_this_week,
        top_sources=top_sources,
        signals_by_tier=signals_by_tier,
        funnel=funnel,
        weekly_activity=weekly_activity,
    )
