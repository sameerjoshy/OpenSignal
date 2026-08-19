"""Weekly digest endpoints - preview + send the learning summary email."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import schemas
from app.database.models import User
from app.database.session import get_db
from app.email import digest as digest_service

router = APIRouter()


@router.get("/digest/preview", response_model=schemas.DigestPreviewOut)
async def preview_digest(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.DigestPreviewOut:
    return await digest_service.build_weekly_digest(db, user)


@router.post("/digest/send", response_model=schemas.DigestSendOut)
async def send_digest(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.DigestSendOut:
    result = await digest_service.send_weekly_digest(db, user)
    return schemas.DigestSendOut(ok=result["ok"], message=result["message"])
