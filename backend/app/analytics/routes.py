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
