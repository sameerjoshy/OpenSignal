"""Reply agent API - list classified inbound replies + auto-draft responses."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import schemas
from app.database.models import Account, EmailMessage, EmailReply, User
from app.database.session import get_db
from app.email import replies as reply_service

router = APIRouter()


@router.get("/replies", response_model=list[schemas.EmailReplyOut])
async def list_replies(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.EmailReplyOut]:
    result = await db.execute(
        select(EmailReply)
        .where(EmailReply.user_id == user.id)
        .order_by(EmailReply.created_at.desc())
        .limit(100)
    )
    replies = result.scalars().all()
    out: list[schemas.EmailReplyOut] = []
    for reply in replies:
        account = None
        original: EmailMessage | None = None
        if reply.email_message_id:
            original = await db.get(EmailMessage, reply.email_message_id)
            if original and original.account_id:
                account = await db.get(Account, original.account_id)
        out.append(
            schemas.EmailReplyOut(
                id=reply.id,
                from_email=reply.from_email,
                subject=reply.subject,
                body=reply.body,
                classification=reply.classification,
                confidence=float(reply.confidence) if reply.confidence else None,
                summary=reply.summary,
                suggested_reply=reply.suggested_reply,
                auto_reply_sent=reply.auto_reply_sent,
                status=reply.status,
                created_at=reply.created_at,
                company_name=account.company_name if account else None,
                original_subject=original.subject if original else None,
            )
        )
    return out


@router.post("/replies/{reply_id}/draft", response_model=schemas.EmailMessageOut)
async def draft_reply(
    reply_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.EmailMessageOut:
    reply = await db.get(EmailReply, reply_id)
    if not reply or reply.user_id != user.id:
        raise HTTPException(status_code=404, detail="Reply not found")
    draft = await reply_service.auto_draft_reply(db, user, reply)
    return schemas.EmailMessageOut.model_validate(draft)
