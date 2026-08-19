"""Inbound reply agent - classify replies via DeepSeek, persist + auto-draft responses."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, EmailMessage, EmailReply, User
from app.services.base import ServiceError
from app.services.credentials import require_key, resolve_credentials
from app.services.deepseek import DeepSeekClient

logger = logging.getLogger("opensignal.replies")


def _domain_from_email(email: str) -> str:
    return (email.rsplit("@", 1)[-1] if "@" in email else email).lower()


async def _find_original_message(db: AsyncSession, user: User, from_email: str) -> EmailMessage | None:
    domain = _domain_from_email(from_email)
    account = None
    if domain:
        result = await db.execute(
            select(Account)
            .where(Account.user_id == user.id, Account.domain.ilike(domain))
            .order_by(Account.created_at.desc())
            .limit(1)
        )
        account = result.scalar_one_or_none()
    stmt = select(EmailMessage).where(
        EmailMessage.user_id == user.id,
        EmailMessage.status.in_(["sent", "opened", "clicked", "replied"]),
    )
    if account:
        stmt = stmt.where(EmailMessage.account_id == account.id)
    else:
        stmt = stmt.where(EmailMessage.to_email == from_email)
    stmt = stmt.order_by(EmailMessage.sent_at.desc()).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def process_inbound_reply(
    db: AsyncSession,
    user: User,
    *,
    from_email: str,
    subject: str | None,
    body: str,
    original_message: EmailMessage | None = None,
) -> EmailReply:
    """Classify an inbound reply, persist it, and draft a suggested response for questions."""
    if not body.strip():
        body = "(empty reply)"
    message = original_message or await _find_original_message(db, user, from_email)

    creds = await resolve_credentials(db, user.id, "deepseek")
    deepseek = DeepSeekClient(require_key(creds, "deepseek"))
    result = await deepseek.classify_reply(subject or "", body)

    suggested_reply: str | None = None
    if result["classification"] in ("question", "hot") and message:
        try:
            suggested_reply = await deepseek.suggest_reply(message.body_text or "", body)
        except ServiceError as exc:
            logger.warning("Reply draft generation failed: %s", exc)

    reply = EmailReply(
        user_id=user.id,
        email_message_id=message.id if message else None,
        from_email=from_email,
        subject=subject,
        body=body[:5000],
        classification=result["classification"],
        confidence=result["confidence"],
        summary=result["summary"],
        suggested_reply=suggested_reply,
        status="classified",
    )
    db.add(reply)
    await db.commit()
    await db.refresh(reply)

    from app.realtime.manager import publish

    await publish(
        "reply_classified",
        {
            "reply_id": str(reply.id),
            "from_email": from_email,
            "classification": reply.classification,
            "summary": reply.summary or "",
        },
    )
    return reply


async def auto_draft_reply(
    db: AsyncSession, user: User, reply: EmailReply, suggested_text: str | None = None
) -> EmailMessage:
    """Create a draft EmailMessage (status draft) so the user can review before sending."""
    text = suggested_text or reply.suggested_reply or ""
    if not text.strip():
        raise ServiceError("No suggested reply available for this message")
    original = await db.get(EmailMessage, reply.email_message_id) if reply.email_message_id else None
    draft = EmailMessage(
        user_id=user.id,
        account_id=original.account_id if original else None,
        campaign_id=original.campaign_id if original else None,
        to_email=reply.from_email,
        subject=f"Re: {reply.subject or original.subject if original else ''}",
        body_text=text,
        status="draft",
    )
    db.add(draft)
    reply.auto_reply_sent = False
    reply.status = "draft-ready"
    await db.commit()
    await db.refresh(draft)
    return draft
