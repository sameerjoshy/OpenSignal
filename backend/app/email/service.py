"""Email execution engine: generate drafts, send via Mailgun/SendGrid, track events."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Account, Campaign, CampaignAccount, EmailEvent, EmailMessage, User
from app.email.generator import build_personalized_email
from app.services.credentials import require_key, resolve_credentials
from app.services.hunter import HunterClient
from app.services.mailgun import MailgunClient
from app.services.sendgrid import SendGridClient
from app.services.base import ServiceError, ServiceNotConfigured

logger = logging.getLogger("opensignal.email")

MESSAGE_STATUSES = {"draft", "queued", "sent", "delivered", "opened", "clicked", "replied", "bounced", "failed"}


async def resolve_contact_email(db: AsyncSession, user: User, account: Account) -> str | None:
    """Resolve a contact email via Hunter, falling back to hello@{domain}."""
    if account.domain:
        creds = await resolve_credentials(db, user.id, "hunter")
        if creds.api_key:
            try:
                client = HunterClient(creds.api_key)
                emails = await client.get_emails(account.domain)
                if emails:
                    return emails[0]
            except Exception as exc:  # noqa: BLE001
                logger.warning("Hunter email lookup failed for %s: %s", account.domain, exc)
        return f"hello@{account.domain}"
    return None


async def generate_message_for_account(
    db: AsyncSession,
    *,
    user: User,
    campaign: Campaign,
    account: Account,
    product_context: str,
    sequence_step: int = 1,
    contact_email: str | None = None,
) -> EmailMessage | None:
    """Generate (via DeepSeek) and persist a draft email for a campaign account."""
    to_email = contact_email or await resolve_contact_email(db, user, account)
    if not to_email:
        logger.warning("No contact email resolvable for %s; skipping generation", account.company_name)
        return None

    result = await build_personalized_email(
        db, user, account, campaign, product_context=product_context, sequence_step=sequence_step
    )

    message = EmailMessage(
        user_id=user.id,
        campaign_id=campaign.id,
        account_id=account.id,
        subject=result.get("subject", ""),
        body_text=result.get("body", ""),
        to_email=to_email,
        status="draft",
        sequence_step=sequence_step,
        provider=None,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def send_message(db: AsyncSession, user: User, message: EmailMessage, provider: str = "mailgun") -> str:
    """Send a single email via the chosen provider and record events."""
    account = None
    if message.account_id:
        account = await crud.get_account(db, message.account_id)
    from_email = f"OpenSignal <hello@opensignal.app>"
    if message.from_email:
        from_email = message.from_email

    provider_id: str = ""
    if provider == "mailgun":
        creds = await resolve_credentials(db, user.id, "mailgun")
        domain = (creds.config or {}).get("domain") or "mail.gtm-360.com"
        client = MailgunClient(require_key(creds, "Mailgun"), domain)
        provider_id = await client.send(
            from_email=f"hello@{domain}",
            to=message.to_email,
            subject=message.subject,
            text=message.body_text,
        )
    elif provider == "sendgrid":
        creds = await resolve_credentials(db, user.id, "sendgrid")
        client = SendGridClient(require_key(creds, "SendGrid"))
        provider_id = await client.send(
            from_email="hello@gtm-360.com",
            to=message.to_email,
            subject=message.subject,
            text=message.body_text,
            custom_args={"opensignal_message_id": str(message.id)},
        )
    else:
        raise ServiceError(f"Unsupported email provider: {provider}")

    message.provider = provider
    message.message_id = provider_id
    message.status = "sent"
    message.sent_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(message)
    await _record_event(db, message, "sent")
    from app.realtime.manager import publish

    await publish("email_sent", {"message_id": str(message.id), "campaign_id": str(message.campaign_id) if message.campaign_id else None, "to_email": message.to_email})
    return provider_id


async def send_campaign_emails(
    db: AsyncSession, user: User, campaign: Campaign, provider: str = "mailgun"
) -> int:
    result = await db.execute(
        select(EmailMessage).where(
            EmailMessage.campaign_id == campaign.id,
            EmailMessage.status.in_(["draft", "queued", "failed"]),
        )
    )
    messages = list(result.scalars().all())
    sent = 0
    for message in messages:
        try:
            await send_message(db, user, message, provider=provider)
            sent += 1
        except ServiceNotConfigured:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Send failed for message %s", message.id)
            message.status = "failed"
            await db.commit()
            await _record_event(db, message, "failed", {"error": str(exc)[:500]})
    return sent


async def _record_event(
    db: AsyncSession, message: EmailMessage, event_type: str, metadata: dict | None = None
) -> EmailEvent:
    event = EmailEvent(email_message_id=message.id, event_type=event_type, meta=metadata)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def apply_event(db: AsyncSession, message: EmailMessage, event_type: str, metadata: dict | None = None) -> None:
    """Apply an inbound webhook event to a message (status + timestamps + event row)."""
    now = datetime.now(timezone.utc)
    mapping = {
        "delivered": "delivered",
        "accepted": "queued",
        "processed": "queued",
        "deferred": "queued",
        "sent": "sent",
        "opened": "opened",
        "open": "opened",
        "click": "clicked",
        "clicked": "clicked",
        "replied": "replied",
        "bounced": "bounced",
        "bounce": "bounced",
        "failed": "failed",
        "dropped": "failed",
        "unsubscribed": "unsubscribed",
        "unsubscribe": "unsubscribed",
        "group_unsubscribe": "unsubscribed",
        "complained": "complained",
        "spamreport": "complained",
    }
    new_status = mapping.get(event_type)
    if new_status and new_status in MESSAGE_STATUSES:
        message.status = new_status
    if event_type in ("opened", "open") and not message.opened_at:
        message.opened_at = now
    if event_type in ("click", "clicked") and not message.clicked_at:
        message.clicked_at = now
    if event_type == "replied" and not message.replied_at:
        message.replied_at = now
    await db.commit()
    await _record_event(db, message, event_type, metadata)
    from app.realtime.manager import publish

    await publish(
        "email_event",
        {
            "message_id": str(message.id),
            "event_type": event_type,
            "status": new_status or message.status,
            "campaign_id": str(message.campaign_id) if message.campaign_id else None,
        },
    )


async def get_message_by_provider_id(db: AsyncSession, provider_id: str) -> EmailMessage | None:
    if not provider_id:
        return None
    clean = provider_id.strip()
    result = await db.execute(select(EmailMessage).where(EmailMessage.message_id == clean).limit(1))
    message = result.scalar_one_or_none()
    if message:
        return message
    # Mailgun wraps ids like <...>; try without angle brackets / trailing domain
    stripped = clean.strip("<>").split("@")[0]
    if stripped and stripped != clean:
        result = await db.execute(
            select(EmailMessage).where(EmailMessage.message_id.like(f"%{stripped}%")).limit(1)
        )
        return result.scalar_one_or_none()
    return None
