from fastapi import APIRouter, Depends
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
