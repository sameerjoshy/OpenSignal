import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crm import service as crm_service
from app.database import schemas
from app.database.models import Campaign, CrmSync, User
from app.database.session import get_db

router = APIRouter()


@router.post("/crm/sync", response_model=dict)
async def sync_to_crm(
    payload: schemas.CrmSyncRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    result = await db.execute(
        select(Campaign).where(Campaign.id == payload.campaign_id, Campaign.user_id == user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    try:
        outcome = await crm_service.sync_campaign(db, user, campaign, payload.service)
        message = (
            f"CRM sync complete: {outcome.get('created', 0)} created, "
            f"{outcome.get('already_synced', 0)} already synced, {outcome.get('errors', 0)} errors"
        )
        return {"service": payload.service, "message": message, **outcome}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/crm/syncs", response_model=list[schemas.CrmSyncOut])
async def list_syncs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.CrmSyncOut]:
    result = await db.execute(
        select(CrmSync).where(CrmSync.user_id == user.id).order_by(CrmSync.created_at.desc()).limit(200)
    )
    return [schemas.CrmSyncOut.model_validate(s) for s in result.scalars().all()]
