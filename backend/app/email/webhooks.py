"""Email webhooks - Mailgun & SendGrid event tracking (opens/clicks/bounces/replies)."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import EmailMessage
from app.database.session import get_db
from app.email.service import apply_event, get_message_by_provider_id
from app.services.credentials import resolve_credentials
from app.services.mailgun import MailgunClient

logger = logging.getLogger("opensignal.email.webhooks")
router = APIRouter()


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
                try:
                    client = MailgunClient(creds.api_key, (creds.config or {}).get("domain", "verify"))
                    if not client.verify_webhook(**signature):
                        raise HTTPException(status_code=403, detail="Invalid signature")
                except HTTPException:
                    raise
                except Exception:  # noqa: BLE001
                    pass  # verification not possible; process anyway (documented MVP behavior)

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
