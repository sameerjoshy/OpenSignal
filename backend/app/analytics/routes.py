import io
import csv

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import service as analytics_service
from app.auth.dependencies import get_current_user
from app.database import schemas
from app.database.models import User
from app.database.session import get_db

router = APIRouter()


@router.get("/analytics", response_model=schemas.AnalyticsOut)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.AnalyticsOut:
    return await analytics_service.build_analytics(db, user)


@router.get("/analytics/outcomes", response_model=schemas.OutcomesOut)
async def get_outcomes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.OutcomesOut:
    return await analytics_service.build_outcomes(db, user)


@router.get("/analytics/learning", response_model=schemas.LearningOut)
async def get_learning(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.LearningOut:
    return await analytics_service.build_learning(db, user)


@router.get("/analytics/export.csv")
async def export_analytics_csv(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """CSV export of the outcomes + engagement metrics (Phase 2: Export & Sharing)."""
    analytics = await analytics_service.build_analytics(db, user)
    outcomes = await analytics_service.build_outcomes(db, user)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["metric", "value"])
    rows = [
        ("signals_total", analytics.total_signals),
        ("signals_this_week", analytics.signals_this_week),
        ("accounts_scored", analytics.total_accounts),
        ("emails_sent", analytics.emails_sent),
        ("emails_opened", analytics.emails_opened),
        ("emails_clicked", analytics.emails_clicked),
        ("emails_replied", analytics.emails_replied),
        ("open_rate_pct", outcomes.open_rate),
        ("reply_rate_pct", outcomes.reply_rate),
        ("click_rate_pct", outcomes.click_rate),
        ("industry_reply_rate_pct", outcomes.industry_reply_rate),
        ("engagement_lift_pct", outcomes.engagement_lift_pct),
        ("pipeline_value", outcomes.pipeline_value),
        ("monthly_forecast", outcomes.monthly_forecast),
        ("deals_estimate", outcomes.deals_estimate),
        ("time_saved_hours", outcomes.time_saved_hours),
        ("labor_value", outcomes.labor_value),
        ("cost_per_meeting", outcomes.cost_per_meeting),
    ]
    writer.writerows(rows)

    response = StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = 'attachment; filename="opensignal_outcomes.csv"'
    return response
