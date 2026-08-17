import uuid

from sqlalchemy import select

from app.database.models import EmailMessage


async def test_apply_event_updates_status_and_timestamp(db):
    message = EmailMessage(
        user_id=uuid.uuid4(),
        subject="Test",
        body_text="Hello",
        to_email="a@example.com",
        status="sent",
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    from app.email.service import apply_event

    await apply_event(db, message, "opened", {"ip": "1.2.3.4"})
    await db.refresh(message)
    assert message.status == "opened"
    assert message.opened_at is not None

    await apply_event(db, message, "clicked")
    await db.refresh(message)
    assert message.status == "clicked"
    assert message.clicked_at is not None

    await apply_event(db, message, "replied")
    await db.refresh(message)
    assert message.status == "replied"


async def test_get_message_by_provider_id(db):
    message = EmailMessage(
        user_id=uuid.uuid4(),
        subject="Track",
        body_text="Body",
        to_email="b@example.com",
        status="sent",
        message_id="<abc123@mailgun.example.com>",
    )
    db.add(message)
    await db.commit()

    from app.email.service import get_message_by_provider_id

    found = await get_message_by_provider_id(db, "abc123@mailgun.example.com")
    assert found is not None
    assert found.id == message.id


async def test_mailgun_webhook_creates_event(client, db):
    message = EmailMessage(
        user_id=uuid.uuid4(),
        subject="Webhook",
        body_text="Body",
        to_email="c@example.com",
        status="sent",
        message_id="wh123@mailgun.example.com",
    )
    db.add(message)
    await db.commit()

    payload = {
        "signature[timestamp]": "1700000000",
        "signature[token]": "tok",
        "signature[signature]": "sig",
        "event-data": (
            '{"event": "opened", "recipient": "c@example.com", '
            '"message": {"headers": {"message-id": "wh123@mailgun.example.com"}}}'
        ),
    }
    resp = await client.post("/api/v1/webhooks/mailgun", data=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    db.expire_all()  # the webhook updated via a different session
    result = await db.execute(
        select(EmailMessage).where(EmailMessage.message_id == "wh123@mailgun.example.com")
    )
    updated = result.scalar_one()
    assert updated.status == "opened"
