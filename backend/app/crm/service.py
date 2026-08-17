"""CRM sync - create leads/contacts/deals in HubSpot or Salesforce and log to crm_syncs."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import Campaign, CampaignAccount, CrmSync, EmailMessage, User
from app.services.credentials import require_key, resolve_credentials
from app.services.hubspot import HubSpotClient
from app.services.salesforce import SalesforceClient

logger = logging.getLogger("opensignal.crm")


async def sync_campaign(db: AsyncSession, user: User, campaign: Campaign, service: str) -> dict:
    """Create a contact/lead for every engaged target, plus a deal for repliers."""
    if service not in ("hubspot", "salesforce"):
        raise ValueError(f"Unsupported CRM service: {service}")

    result = {"created": 0, "already_synced": 0, "errors": 0}
    stmt = select(CampaignAccount).where(CampaignAccount.campaign_id == campaign.id)
    targets = list((await db.execute(stmt)).scalars().all())

    for target in targets:
        account = await crud.get_account(db, target.account_id)
        if not account:
            continue

        already = await db.execute(
            select(CrmSync).where(
                CrmSync.campaign_id == campaign.id,
                CrmSync.account_id == account.id,
                CrmSync.service == service,
                CrmSync.status == "synced",
            )
        )
        if already.scalar_one_or_none():
            result["already_synced"] += 1
            continue

        replied = await _has_replied(db, campaign.id, account.id)
        try:
            external_id = await _create_record(db, user, service, account, replied)
            db.add(
                CrmSync(
                    user_id=user.id,
                    campaign_id=campaign.id,
                    account_id=account.id,
                    service=service,
                    status="synced",
                    object_type="opportunity" if replied else ("deal" if service == "hubspot" else "lead"),
                    external_id=external_id,
                    synced_at=datetime.now(timezone.utc),
                )
            )
            result["created"] += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("CRM sync failed for %s", account.company_name)
            db.add(
                CrmSync(
                    user_id=user.id,
                    campaign_id=campaign.id,
                    account_id=account.id,
                    service=service,
                    status="error",
                    error_message=str(exc)[:500],
                )
            )
            result["errors"] += 1
        await db.commit()
    return result


async def _has_replied(db: AsyncSession, campaign_id, account_id) -> bool:
    result = await db.execute(
        select(EmailMessage).where(
            EmailMessage.campaign_id == campaign_id,
            EmailMessage.account_id == account_id,
            EmailMessage.status == "replied",
        )
    )
    return result.scalar_one_or_none() is not None


async def _create_record(db: AsyncSession, user: User, service: str, account, replied: bool) -> str:
    company = account.company_name
    email = f"hello@{account.domain}" if account.domain else ""

    if service == "hubspot":
        creds = await resolve_credentials(db, user.id, "hubspot")
        client = HubSpotClient(require_key(creds, "HubSpot"))
        contact_id = await client.create_contact(email=email, company=company)
        if replied:
            return await client.create_deal(
                deal_name=f"{company} - OpenSignal reply",
                amount=float(account.revenue) if account.revenue else None,
                contact_id=contact_id,
            )
        return contact_id

    creds = await resolve_credentials(db, user.id, "salesforce")
    cfg = creds.config or {}
    client = SalesforceClient(
        require_key(creds, "Salesforce"),
        cfg.get("client_secret"),
        cfg.get("username"),
        cfg.get("password"),
    )
    return await client.create_lead(
        company=company,
        email=email,
        description=f"Replied to OpenSignal campaign" if replied else "Synced from OpenSignal",
    )
