"""Campaign orchestration: create, import targets, route by tier, generate + send email sequence."""

import datetime as dt
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaigns.importer import extract_emails, parse_csv, parse_email_file
from app.database import crud
from app.database.models import Campaign, CampaignAccount, User
from app.database.session import AsyncSessionLocal
from app.email.service import generate_message_for_account
from app.services.base import ServiceError

logger = logging.getLogger("opensignal.campaigns")

DEFAULT_CHANNELS = {"email": True, "linkedin": False, "call": False}
DEFAULT_CADENCE = {"step_interval_days": 2, "max_steps": 3}
STATUS_ORDER = ["draft", "active", "paused", "completed", "archived"]


async def import_companies(db: AsyncSession, user: User, campaign: Campaign, companies: list[str]) -> int:
    """Create accounts + campaign_accounts for a list of company names."""
    imported = 0
    for name in companies:
        account = await crud.find_or_create_account(db, user.id, name)
        exists = await db.execute(
            select(CampaignAccount).where(
                CampaignAccount.campaign_id == campaign.id, CampaignAccount.account_id == account.id
            )
        )
        if exists.scalar_one_or_none():
            continue
        db.add(CampaignAccount(campaign_id=campaign.id, account_id=account.id))
        imported += 1
    await db.commit()
    return imported


async def import_csv(db: AsyncSession, user: User, campaign: Campaign, content: bytes) -> int:
    rows = parse_csv(content)
    imported = 0
    for row in rows[:500]:
        account = await crud.find_or_create_account(
            db, user.id, row["company_name"], domain=row.get("domain")
        )
        exists = await db.execute(
            select(CampaignAccount).where(
                CampaignAccount.campaign_id == campaign.id, CampaignAccount.account_id == account.id
            )
        )
        if exists.scalar_one_or_none():
            continue
        db.add(CampaignAccount(campaign_id=campaign.id, account_id=account.id))
        imported += 1
    await db.commit()
    return imported


async def import_email_addresses(db: AsyncSession, user: User, campaign: Campaign, emails: list[str]) -> int:
    """Import a list of email addresses, creating accounts by domain and pinning the recipient."""
    imported = 0
    for email in emails[:500]:
        email = (email or "").strip().lower()
        if "@" not in email:
            continue
        domain = email.rsplit("@", 1)[1].strip(".")
        if not domain:
            continue
        account = await crud.find_or_create_account(db, user.id, domain, domain=domain)
        target = (
            await db.execute(
                select(CampaignAccount).where(
                    CampaignAccount.campaign_id == campaign.id,
                    CampaignAccount.account_id == account.id,
                )
            )
        ).scalar_one_or_none()
        if target:
            if target.contact_email != email:
                target.contact_email = email
                await db.commit()
        else:
            db.add(
                CampaignAccount(
                    campaign_id=campaign.id,
                    account_id=account.id,
                    contact_email=email,
                    status="ready",
                )
            )
            imported += 1
    await db.commit()
    return imported


async def run_campaign(db: AsyncSession, user: User, campaign: Campaign) -> dict:
    """Detect signals, score accounts, route by tier, and generate first email for each target."""
    from app.signals import detector, scorer

    result = {"processed": 0, "signals": 0, "scored": 0, "generated": 0, "errors": 0}
    stmt = select(CampaignAccount).where(CampaignAccount.campaign_id == campaign.id)
    targets = list((await db.execute(stmt)).scalars().all())

    channels = campaign.channels or DEFAULT_CHANNELS
    cadence = campaign.cadence or DEFAULT_CADENCE
    max_steps = int(cadence.get("max_steps", 3))
    product_context = campaign.description or "our B2B product"

    for target in targets:
        try:
            account = await crud.get_account_for_user(db, user.id, target.account_id)
            if not account:
                continue
            created = await detector.detect_for_account(db, user, account)
            result["signals"] += len(created)

            score_result = await scorer.score_account(db, user, account)
            result["scored"] += 1

            target.score = account.score
            target.tier = account.tier
            target.status = "ready"
            await db.commit()

            tier = account.tier or 3
            step_limit = 1 if tier == 3 else max_steps

            if channels.get("email", True):
                message = await generate_message_for_account(
                    db,
                    user=user,
                    campaign=campaign,
                    account=account,
                    product_context=product_context,
                    sequence_step=1,
                    contact_email=target.contact_email,
                )
                if message:
                    result["generated"] += 1
            result["processed"] += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("Campaign run failed for target %s", target.id)
            target.status = "error"
            target.error = str(exc)[:500]
            await db.commit()
            result["errors"] += 1

    campaign.status = "active"
    result["message"] = (
        f"Processed {result['processed']} target(s): {result['signals']} signals, "
        f"{result['scored']} scored, {result['generated']} emails generated, {result['errors']} errors"
    )
    campaign.last_run_at = dt.datetime.now(dt.timezone.utc)
    campaign.run_log = result["message"]
    await db.commit()
    from app.realtime.manager import publish

    await publish(
        "campaign_run",
        {
            "campaign_id": str(campaign.id),
            "processed": result["processed"],
            "signals": result["signals"],
            "generated": result["generated"],
            "errors": result["errors"],
        },
    )
    return result


async def run_campaign_in_background(campaign_id, user_id) -> dict:
    """Run a campaign with its own DB session (safe for detached execution)."""
    try:
        async with AsyncSessionLocal() as db:
            user = await db.get(User, user_id)
            campaign = await db.get(Campaign, campaign_id)
            if not user or not campaign:
                logger.warning("Campaign background run skipped: user or campaign missing")
                return {"processed": 0, "errors": 1, "message": "Campaign or user not found"}
            return await run_campaign(db, user, campaign)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Campaign background run failed: %s", campaign_id)
        try:
            async with AsyncSessionLocal() as db:
                campaign = await db.get(Campaign, campaign_id)
                if campaign:
                    campaign.status = "active"
                    campaign.run_log = f"Background run failed: {str(exc)[:300]}"
                    await db.commit()
        except Exception:  # noqa: BLE001
            pass
        return {"processed": 0, "errors": 1, "message": f"Background run failed: {str(exc)[:300]}"}


def extract_email_list(text_or_emails: str | list[str]) -> list[str]:
    """Normalize either pasted text or an already-split email list into unique addresses."""
    if isinstance(text_or_emails, list):
        return extract_emails("\n".join(e for e in text_or_emails if e))
    return extract_emails(text_or_emails)


def extract_email_list_from_file(content: bytes, filename: str) -> list[str]:
    return parse_email_file(content, filename)


def validate_status_change(current: str, new: str) -> None:
    if current == new:
        return
    allowed = {
        "draft": {"active", "archived"},
        "active": {"paused", "completed", "archived"},
        "paused": {"active", "completed", "archived"},
        "completed": {"active"},
        "archived": set(),
    }
    if new not in allowed.get(current, set()):
        raise ServiceError(f"Cannot change campaign status from '{current}' to '{new}'")
