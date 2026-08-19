import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud, schemas
from app.database.models import Account, Signal, User
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.signals import detector, scorer
from app.analytics import service as analytics_service
from app.services.orchestration import route_campaign
from app.services.base import ServiceError
from app.services.credentials import require_key, resolve_credentials

router = APIRouter()


# ---------------------------------------------------------------- Accounts
@router.get("/accounts", response_model=list[schemas.AccountOut])
async def list_accounts(
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.AccountOut]:
    accounts = await crud.list_accounts(db, user.id, limit=limit, offset=offset)
    return [schemas.AccountOut.model_validate(a) for a in accounts]


@router.post("/accounts", response_model=schemas.AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: schemas.AccountIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.AccountOut:
    account = await crud.find_or_create_account(
        db,
        user.id,
        payload.company_name,
        domain=payload.domain,
        industry=payload.industry,
        employee_count=payload.employee_count,
        revenue=payload.revenue,
        location=payload.location,
        website=payload.website,
    )
    return schemas.AccountOut.model_validate(account)


@router.get("/accounts/{account_id}", response_model=schemas.AccountOut)
async def get_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.AccountOut:
    account = await crud.get_account_for_user(db, user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return schemas.AccountOut.model_validate(account)


@router.get("/accounts/{account_id}/orchestration", response_model=dict)
async def account_orchestration(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Omnichannel routing plan for this account based on its buying-intent tier."""
    account = await crud.get_account_for_user(db, user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    channels = route_campaign(account)
    return {
        "account_id": account.id,
        "tier": account.tier,
        "channels": channels,
        "note": "Email is live today; SMS / Slack / LinkedIn are reserved for future channel adapters.",
    }


@router.get("/accounts/{account_id}/intelligence", response_model=schemas.AccountIntelligenceOut)
async def account_intelligence(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.AccountIntelligenceOut:
    try:
        return await analytics_service.build_account_intelligence(db, user, account_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/accounts/{account_id}/signals", response_model=list[schemas.SignalOut])
async def account_signals(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.SignalOut]:
    account = await crud.get_account_for_user(db, user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    signals = await crud.list_signals(db, user.id, account_id=account_id)
    return [schemas.SignalOut.model_validate(s) for s in signals]


@router.post("/accounts/{account_id}/detect", response_model=list[schemas.SignalOut])
async def detect_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.SignalOut]:
    account = await crud.get_account_for_user(db, user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    created = await detector.detect_for_account(db, user, account)
    return [schemas.SignalOut.model_validate(s) for s in created]


@router.post("/accounts/{account_id}/score", response_model=dict)
async def score_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    account = await crud.get_account_for_user(db, user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return await scorer.score_account(db, user, account)


# ---------------------------------------------------------------- Signals
@router.get("/signals", response_model=list[schemas.SignalWithAccountOut])
async def list_signals(
    source: str | None = None,
    signal_type: str | None = None,
    tier: int | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[schemas.SignalWithAccountOut]:
    signals = await crud.list_signals(
        db, user.id, source=source, signal_type=signal_type, tier=tier, limit=limit, offset=offset
    )
    result = []
    for s in signals:
        item = schemas.SignalWithAccountOut.model_validate(s)
        item.account_name = s.account.company_name
        item.account_tier = s.account.tier
        item.account_score = float(s.account.score) if s.account.score is not None else None
        result.append(item)
    return result


@router.post("/signals", response_model=schemas.SignalOut, status_code=status.HTTP_201_CREATED)
async def create_manual_signal(
    payload: schemas.SignalIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.SignalOut:
    account = await crud.get_account_for_user(db, user.id, payload.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    signal = await crud.create_signal(
        db,
        user_id=user.id,
        account_id=payload.account_id,
        source=payload.source,
        signal_type=payload.signal_type,
        title=payload.title,
        description=payload.description,
        url=payload.url,
    )
    return schemas.SignalOut.model_validate(signal)


# ---------------------------------------------------------------- Contacts (Apollo)
@router.get("/contacts/search")
async def search_contacts(
    company: str = Query(..., min_length=2),
    titles: str | None = Query(None, description="Comma-separated job titles to target"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    """Apollo People Search - find decision-makers at a company."""
    from app.services.apollo import ApolloClient

    creds = await resolve_credentials(db, user.id, "apollo")
    client = ApolloClient(require_key(creds, "apollo"))
    try:
        title_list = [t.strip() for t in titles.split(",") if t.strip()] if titles else None
        return await client.search_contacts(company, title_list, limit=limit)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/contacts/enrich")
async def enrich_contact(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Apollo Enrichment - resolve role + company details from a single email."""
    from app.services.apollo import ApolloClient

    email = (payload.get("email") or "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email is required")
    creds = await resolve_credentials(db, user.id, "apollo")
    client = ApolloClient(require_key(creds, "apollo"))
    try:
        return await client.enrich_contact(email)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
