"""Follow-up endpoints - see who clicked but didn't reply, and send a step-2 nudge."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.email import followup as followup_service

router = APIRouter()


@router.get("/follow-ups")
async def list_follow_ups(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    return await followup_service.list_follow_ups(db, user, limit=limit)


@router.post("/follow-ups/{message_id}/send")
async def send_follow_up(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    try:
        return await followup_service.send_follow_up(db, user, message_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc