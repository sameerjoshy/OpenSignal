"""Settings routes: connect/test services, manage account, view usage."""

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import crud, schemas
from app.database.models import EmailMessage, User
from app.database.session import get_db
from app.security.encryption import encrypt_config, encrypt_value
from app.services.base import ServiceError
from app.services.connection import test_service
from app.services.registry import SERVICES, SERVICE_BY_ID
from config import settings

router = APIRouter()


class ServiceStatusOut(BaseModel):
    service: str
    name: str
    description: str
    free_tier_note: str
    connected: bool
    source: str  # "user" | "env" | "none"
    validated_at: str | None = None


class SaveServiceIn(BaseModel):
    service: str
    api_key: str = ""
    config: dict[str, Any] | None = None


class QuotaOut(BaseModel):
    service: str
    name: str
    note: str
    usage: int | None = None


@router.get("/settings/services", response_model=list[ServiceStatusOut])
async def list_services(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ServiceStatusOut]:
    credentials = await crud.list_credentials(db, user.id)
    by_service = {c.service: c for c in credentials}
    result = []
    for meta in SERVICES:
        cred = by_service.get(meta.id)
        source = "none"
        if cred:
            source = "user"
        elif getattr(settings, meta.env_api_key, ""):
            source = "env"
        result.append(
            ServiceStatusOut(
                service=meta.id,
                name=meta.name,
                description=meta.description,
                free_tier_note=meta.free_tier_note,
                connected=source != "none",
                source=source,
                validated_at=cred.validated_at.isoformat() if cred and cred.validated_at else None,
            )
        )
    return result


@router.post("/settings/services", response_model=schemas.ServiceTestOut, status_code=status.HTTP_201_CREATED)
async def save_service(
    payload: SaveServiceIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.ServiceTestOut:
    if payload.service not in SERVICE_BY_ID:
        raise HTTPException(status_code=400, detail=f"Unknown service: {payload.service}")
    if not payload.api_key and not payload.config:
        raise HTTPException(status_code=400, detail="API key or config is required")

    encrypted = encrypt_value(payload.api_key) if payload.api_key else ""
    stored_config = encrypt_config(payload.config or {})
    cred = await crud.upsert_credential(db, user.id, payload.service, encrypted, stored_config)

    try:
        result = await test_service(db, user.id, payload.service)
        cred.validated_at = dt.datetime.now(dt.timezone.utc)
        await db.commit()
        return schemas.ServiceTestOut(service=payload.service, ok=True, message=result["message"], quota=result.get("quota"))
    except ServiceError as exc:
        cred.is_active = False
        await db.commit()
        return schemas.ServiceTestOut(service=payload.service, ok=False, message=exc.message)


@router.post("/settings/services/{service}/test", response_model=schemas.ServiceTestOut)
async def test_saved_service(
    service: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.ServiceTestOut:
    try:
        result = await test_service(db, user.id, service)
        return schemas.ServiceTestOut(service=service, ok=True, message=result["message"], quota=result.get("quota"))
    except ServiceError as exc:
        return schemas.ServiceTestOut(service=service, ok=False, message=exc.message)


@router.delete("/settings/services/{service}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    await crud.delete_credential(db, user.id, service)


@router.get("/settings/account", response_model=schemas.UserOut)
async def get_account(user: User = Depends(get_current_user)) -> schemas.UserOut:
    return schemas.UserOut.model_validate(user)


@router.patch("/settings/account", response_model=schemas.UserOut)
async def update_account(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.UserOut:
    full_name = payload.get("full_name")
    if full_name:
        user.full_name = str(full_name)[:255]
    await db.commit()
    await db.refresh(user)
    return schemas.UserOut.model_validate(user)


@router.get("/settings/quota", response_model=list[QuotaOut])
async def get_quota(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[QuotaOut]:
    month_start = dt.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count()).select_from(EmailMessage).where(
            EmailMessage.user_id == user.id, EmailMessage.created_at >= month_start
        )
    )
    emails_this_month = int(result.scalar_one())
    return [
        QuotaOut(service="mailgun", name="Mailgun", note="1000 emails/month free", usage=emails_this_month),
        QuotaOut(service="sendgrid", name="SendGrid", note="100 emails/day free", usage=emails_this_month),
        QuotaOut(service="apollo", name="Apollo", note="50 searches/month free"),
        QuotaOut(service="hunter", name="Hunter", note="50 searches/month free"),
        QuotaOut(service="newsapi", name="NewsAPI", note="100 requests/day free"),
        QuotaOut(service="sec_edgar", name="SEC EDGAR", note="Unlimited, public API"),
    ]
