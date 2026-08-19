import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.campaigns import service as campaign_service
from app.auth.dependencies import get_current_user
from app.database import crud, schemas
from app.database.models import Campaign, CampaignAccount, EmailMessage, User
from app.database.session import get_db
from app.email.service import send_campaign_emails

router = APIRouter()


@router.get("/campaigns", response_model=list[schemas.CampaignOut])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.CampaignOut]:
    result = await db.execute(
        select(Campaign).where(Campaign.user_id == user.id).order_by(Campaign.created_at.desc())
    )
    return [schemas.CampaignOut.model_validate(c) for c in result.scalars().all()]


@router.post("/campaigns", response_model=schemas.CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: schemas.CampaignIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignOut:
    campaign = Campaign(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        tier_filters=payload.tier_filters,
        channels=payload.channels,
        cadence=payload.cadence,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return schemas.CampaignOut.model_validate(campaign)


@router.get("/campaigns/{campaign_id}", response_model=schemas.CampaignDetailOut)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignDetailOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    detail = schemas.CampaignDetailOut.model_validate(campaign)

    detail.account_count = await crud.count(db, CampaignAccount, campaign_id=campaign_id)
    detail.sent_count = await crud.count(db, EmailMessage, campaign_id=campaign_id, status="sent")
    detail.open_count = await crud.count(db, EmailMessage, campaign_id=campaign_id, status="opened")
    detail.click_count = await crud.count(db, EmailMessage, campaign_id=campaign_id, status="clicked")
    detail.reply_count = await crud.count(db, EmailMessage, campaign_id=campaign_id, status="replied")
    return detail


@router.patch("/campaigns/{campaign_id}", response_model=schemas.CampaignOut)
async def update_campaign(
    campaign_id: uuid.UUID,
    payload: schemas.CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] != campaign.status:
        campaign_service.validate_status_change(campaign.status, data["status"])
    for key, value in data.items():
        setattr(campaign, key, value)
    await db.commit()
    await db.refresh(campaign)
    return schemas.CampaignOut.model_validate(campaign)


@router.post("/campaigns/{campaign_id}/import", response_model=schemas.CampaignRunOut)
async def import_campaign_companies(
    campaign_id: uuid.UUID,
    payload: schemas.CampaignImportIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    imported = await campaign_service.import_companies(db, user, campaign, payload.companies)
    return schemas.CampaignRunOut(campaign_id=campaign_id, queued=imported, message=f"Imported {imported} companies")


@router.post("/campaigns/{campaign_id}/import-csv", response_model=schemas.CampaignRunOut)
async def import_campaign_csv(
    campaign_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    content = await file.read()
    imported = await campaign_service.import_csv(db, user, campaign, content)
    return schemas.CampaignRunOut(campaign_id=campaign_id, queued=imported, message=f"Imported {imported} companies")


@router.post("/campaigns/{campaign_id}/import-emails", response_model=schemas.CampaignRunOut)
async def import_campaign_emails(
    campaign_id: uuid.UUID,
    payload: schemas.CampaignEmailsIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    emails = campaign_service.extract_email_list(payload.emails)
    imported = await campaign_service.import_email_addresses(db, user, campaign, emails)
    return schemas.CampaignRunOut(campaign_id=campaign_id, queued=imported, message=f"Imported {imported} email addresses")


@router.post("/campaigns/{campaign_id}/import-emails-file", response_model=schemas.CampaignRunOut)
async def import_campaign_emails_file(
    campaign_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    content = await file.read()
    emails = campaign_service.extract_email_list_from_file(content, file.filename or "")
    imported = await campaign_service.import_email_addresses(db, user, campaign, emails)
    return schemas.CampaignRunOut(campaign_id=campaign_id, queued=imported, message=f"Imported {imported} email addresses")


@router.post("/campaigns/{campaign_id}/run", response_model=schemas.CampaignRunOut)
async def run_campaign(
    campaign_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    target_count = (
        await db.execute(
            select(func.count()).select_from(CampaignAccount).where(CampaignAccount.campaign_id == campaign.id)
        )
    ).scalar_one()
    background_tasks.add_task(campaign_service.run_campaign_in_background, campaign.id, user.id)
    return schemas.CampaignRunOut(
        campaign_id=campaign_id,
        queued=int(target_count),
        message=f"Campaign run started in the background for {target_count} target(s). Check back shortly.",
    )


@router.post("/campaigns/{campaign_id}/send", response_model=schemas.CampaignRunOut)
async def send_campaign(
    campaign_id: uuid.UUID,
    provider: str = "mailgun",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.CampaignRunOut:
    campaign = await _get_campaign_or_404(db, user.id, campaign_id)
    sent = await send_campaign_emails(db, user, campaign, provider=provider)
    return schemas.CampaignRunOut(
        campaign_id=campaign_id, queued=sent, message=f"Sent {sent} emails via {provider}"
    )


@router.get("/campaigns/{campaign_id}/accounts", response_model=list[schemas.CampaignAccountOut])
async def campaign_accounts(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.CampaignAccountOut]:
    await _get_campaign_or_404(db, user.id, campaign_id)
    result = await db.execute(
        select(CampaignAccount)
        .where(CampaignAccount.campaign_id == campaign_id)
        .options(selectinload(CampaignAccount.account))
        .order_by(CampaignAccount.created_at.desc())
    )
    rows = result.scalars().all()
    out = []
    for row in rows:
        item = schemas.CampaignAccountOut.model_validate(row)
        item.account = schemas.AccountOut.model_validate(row.account)
        out.append(item)
    return out


@router.get("/campaigns/{campaign_id}/emails", response_model=list[schemas.EmailMessageOut])
async def campaign_emails(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.EmailMessageOut]:
    await _get_campaign_or_404(db, user.id, campaign_id)
    result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.campaign_id == campaign_id)
        .order_by(EmailMessage.created_at.desc())
        .limit(500)
    )
    return [schemas.EmailMessageOut.model_validate(m) for m in result.scalars().all()]


async def _get_campaign_or_404(db: AsyncSession, user_id, campaign_id: uuid.UUID) -> Campaign:
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign
