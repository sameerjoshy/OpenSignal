import io
import csv
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics import service as analytics_service
from app.auth.dependencies import get_current_user
from app.database import schemas
from app.database.models import User
from app.database.session import get_db
from config import settings

router = APIRouter()

SHARE_TTL_SECONDS = 7 * 24 * 3600  # 7 days


def _sign(payload: str) -> str:
    return hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


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


@router.post("/analytics/share")
async def create_share_link(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Create a 7-day read-only share link to the outcomes dashboard."""
    expires = int(time.time()) + SHARE_TTL_SECONDS
    payload = json.dumps({"uid": str(user.id), "exp": expires}, separators=(",", ":"))
    token = f"{_sign(payload)}.{payload}"
    return {"url": f"/api/v1/analytics/shared/{token}", "expires_at": datetime.fromtimestamp(expires, tz=timezone.utc).isoformat()}


@router.get("/analytics/shared/{token}")
async def shared_outcomes(token: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Read-only outcomes view for stakeholders (no auth)."""
    try:
        sig, payload_b64 = token.split(".", 1)
        payload = json.loads(payload_b64)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=400, detail="Invalid share link")
    if not hmac.compare_digest(_sign(payload_b64), sig):
        raise HTTPException(status_code=400, detail="Invalid share link")
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=410, detail="This share link has expired")
    try:
        user_id = uuid.UUID(payload["uid"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid share link")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    analytics = await analytics_service.build_analytics(db, user)
    outcomes = await analytics_service.build_outcomes(db, user)
    return {"shared_by": user.full_name or user.email, "analytics": analytics, "outcomes": outcomes}
