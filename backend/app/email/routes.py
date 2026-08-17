import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import schemas
from app.database.models import EmailEvent, EmailMessage, EmailTemplate, User
from app.database.session import get_db

router = APIRouter()


@router.get("/email/messages", response_model=list[schemas.EmailMessageOut])
async def list_email_messages(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.EmailMessageOut]:
    result = await db.execute(
        select(EmailMessage)
        .where(EmailMessage.user_id == user.id)
        .order_by(EmailMessage.created_at.desc())
        .limit(min(limit, 500))
    )
    return [schemas.EmailMessageOut.model_validate(m) for m in result.scalars().all()]


@router.get("/email/messages/{message_id}", response_model=schemas.EmailMessageOut)
async def get_email_message(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.EmailMessageOut:
    message = await db.get(EmailMessage, message_id)
    if not message or message.user_id != user.id:
        raise HTTPException(status_code=404, detail="Email not found")
    return schemas.EmailMessageOut.model_validate(message)


@router.get("/email/messages/{message_id}/events", response_model=list[schemas.EmailEventOut])
async def get_email_events(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.EmailEventOut]:
    message = await db.get(EmailMessage, message_id)
    if not message or message.user_id != user.id:
        raise HTTPException(status_code=404, detail="Email not found")
    result = await db.execute(
        select(EmailEvent).where(EmailEvent.email_message_id == message_id).order_by(EmailEvent.occurred_at)
    )
    return [schemas.EmailEventOut.model_validate(e) for e in result.scalars().all()]


# ---------------------------------------------------------------- Templates
@router.get("/email/templates", response_model=list[schemas.EmailTemplateOut])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.EmailTemplateOut]:
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.user_id == user.id).order_by(EmailTemplate.sequence_step)
    )
    return [schemas.EmailTemplateOut.model_validate(t) for t in result.scalars().all()]


@router.post("/email/templates", response_model=schemas.EmailTemplateOut, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: schemas.EmailTemplateIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.EmailTemplateOut:
    template = EmailTemplate(
        user_id=user.id,
        name=payload.name,
        subject=payload.subject,
        body=payload.body,
        sequence_step=payload.sequence_step,
        is_default=payload.is_default,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return schemas.EmailTemplateOut.model_validate(template)


@router.delete("/email/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == template_id, EmailTemplate.user_id == user.id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(template)
    await db.commit()
