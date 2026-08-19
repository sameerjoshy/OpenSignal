"""Email webhooks - Mailgun & SendGrid event tracking (opens/clicks/bounces/replies)."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import EmailMessage, User
from app.database.session import get_db
from app.email.replies import process_inbound_reply
from app.email.service import apply_event, get_message_by_provider_id
from app.services.credentials import resolve_credentials
from app.services.mailgun import MailgunClient

logger = logging.getLogger("opensignal.email.webhooks")
router = APIRouter()


@router.post("/webhooks/mailgun/inbound")
async def mailgun_inbound(request: Request, db: AsyncSession = Depends(get_db)):
    """Inbound route target - receives full replies and runs the reply agent."""
    form = await request.form()
    signature = {
        "timestamp": form.get("signature[timestamp]", ""),
        "token": form.get("signature[token]", ""),
        "signature": form.get("signature[signature]", ""),
    }

    # Best-effort signature verification when the sender signs the request.
    if signature["signature"]:
        recipient = form.get("recipient", "") or form.get("To", "")
        message_id = form.get("Message-Id", "")
        user_id = await _owner_of(db, message_id, recipient)
        if user_id:
            creds = await resolve_credentials(db, user_id, "mailgun")
            if creds.api_key:
                client = MailgunClient(creds.api_key, (creds.config or {}).get("domain", "verify"))
                if not client.verify_webhook(**signature):
                    raise HTTPException(status_code=403, detail="Invalid signature")
            else:
                raise HTTPException(status_code=403, detail="No Mailgun key configured")
    else:
        raise HTTPException(status_code=403, detail="Missing signature")

    from_email = (form.get("From") or "").strip()
    subject = (form.get("Subject") or "").strip() or None
    body = form.get("stripped-text") or form.get("body-plain") or form.get("body-html") or ""
    if not from_email or not body:
        raise HTTPException(status_code=400, detail="Missing From or body")

    user_id = await _owner_of(db, form.get("Message-Id", ""), from_email)
    if not user_id:
        # Fall back to resolving the owner from the recipient mailbox address.
        recipient = (form.get("To") or "").strip()
        user_id = await _owner_of(db, "", recipient)
    if not user_id:
        logger.warning("Inbound reply for unknown owner: %s", from_email)
        return {"status": "ok", "processed": False}

    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return {"status": "ok", "processed": False}
        reply = await process_inbound_reply(session, user, from_email=from_email, subject=subject, body=body)
        logger.info("Inbound reply classified as %s: %s", reply.classification, reply.from_email)
    return {"status": "ok", "processed": True}


@router.post("/webhooks/mailgun")
async def mailgun_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    signature = {
        "timestamp": form.get("signature[timestamp]", ""),
        "token": form.get("signature[token]", ""),
        "signature": form.get("signature[signature]", ""),
    }
    event_data_raw = form.get("event-data", "")
    try:
        event_data = json.loads(event_data_raw) if event_data_raw else {}
    except json.JSONDecodeError:
        event_data = {}

    message_id = ((event_data.get("message") or {}).get("headers") or {}).get("message-id", "")
    recipient = event_data.get("recipient", "")

    # Best-effort signature verification using the user's Mailgun key.
    if message_id or recipient:
        user_id = await _owner_of(db, message_id, recipient)
        if user_id:
            creds = await resolve_credentials(db, user_id, "mailgun")
            if creds.api_key:
                client = MailgunClient(creds.api_key, (creds.config or {}).get("domain", "verify"))
                if not client.verify_webhook(**signature):
                    raise HTTPException(status_code=403, detail="Invalid signature")
            else:
                logger.warning("No Mailgun key resolvable for signature verification; rejecting webhook")
                raise HTTPException(status_code=403, detail="No Mailgun key configured")

    event_type = event_data.get("event", "")
    message = await get_message_by_provider_id(db, message_id)
    if message:
        await apply_event(db, message, event_type, {"payload": event_data})
        logger.info("Mailgun event %s applied to %s", event_type, message.id)
    else:
        logger.warning("Mailgun event for unknown message: %s", message_id)
    return {"status": "ok"}

@router.post("/webhooks/sendgrid")
async def sendgrid_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    if not isinstance(body, list):
        raise HTTPException(status_code=400, detail="Expected an array of events")

    processed = 0
    for event in body:
        message = None
        unique_args = event.get("unique_args") or {}
        opensignal_id = unique_args.get("opensignal_message_id")
        if opensignal_id:
            try:
                message = await db.get(EmailMessage, uuid.UUID(str(opensignal_id)))
            except ValueError:
                message = None
        if message is None:
            message = await get_message_by_provider_id(db, event.get("sg_message_id", ""))
        if message:
            await apply_event(db, message, event.get("event", ""), {"payload": event})
            processed += 1
    return {"status": "ok", "processed": processed}


async def _owner_of(db: AsyncSession, message_id: str, recipient: str):
    message = await get_message_by_provider_id(db, message_id)
    if message:
        return message.user_id
    return None
