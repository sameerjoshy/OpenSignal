import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import models as m
from app.database.models import Account, Signal, SignalScore, User


# ---------------------------------------------------------------- Users
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_supabase_id(db: AsyncSession, supabase_id: str) -> User | None:
    result = await db.execute(select(User).where(User.supabase_auth_id == supabase_id))
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def upsert_supabase_user(db: AsyncSession, email: str, supabase_id: str, full_name: str | None = None) -> User:
    user = await get_user_by_supabase_id(db, supabase_id)
    if user:
        user.email = email
        if full_name:
            user.full_name = full_name
        await db.commit()
        await db.refresh(user)
        return user
    user = await get_user_by_email(db, email)
    if user:
        user.supabase_auth_id = supabase_id
        if full_name:
            user.full_name = full_name
        await db.commit()
        await db.refresh(user)
        return user
    user = User(email=email, full_name=full_name, supabase_auth_id=supabase_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ---------------------------------------------------------------- Credentials
async def get_credential(db: AsyncSession, user_id: uuid.UUID, service: str) -> m.ServiceCredential | None:
    result = await db.execute(
        select(m.ServiceCredential).where(
            m.ServiceCredential.user_id == user_id, m.ServiceCredential.service == service
        )
    )
    return result.scalar_one_or_none()


async def list_credentials(db: AsyncSession, user_id: uuid.UUID) -> list[m.ServiceCredential]:
    result = await db.execute(select(m.ServiceCredential).where(m.ServiceCredential.user_id == user_id))
    return list(result.scalars().all())


async def upsert_credential(
    db: AsyncSession,
    user_id: uuid.UUID,
    service: str,
    encrypted_key: str,
    config: dict | None = None,
) -> m.ServiceCredential:
    cred = await get_credential(db, user_id, service)
    if cred:
        cred.encrypted_key = encrypted_key
        cred.config = config
        cred.is_active = True
    else:
        cred = m.ServiceCredential(user_id=user_id, service=service, encrypted_key=encrypted_key, config=config)
        db.add(cred)
    await db.commit()
    await db.refresh(cred)
    return cred


async def delete_credential(db: AsyncSession, user_id: uuid.UUID, service: str) -> bool:
    result = await db.execute(
        delete(m.ServiceCredential).where(
            m.ServiceCredential.user_id == user_id, m.ServiceCredential.service == service
        )
    )
    await db.commit()
    return result.rowcount > 0


# ---------------------------------------------------------------- Accounts
async def get_account(db: AsyncSession, account_id: uuid.UUID) -> Account | None:
    return await db.get(Account, account_id)


async def get_account_for_user(db: AsyncSession, user_id: uuid.UUID, account_id: uuid.UUID) -> Account | None:
    result = await db.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
    return result.scalar_one_or_none()


async def list_accounts(db: AsyncSession, user_id: uuid.UUID, limit: int = 200, offset: int = 0) -> list[Account]:
    result = await db.execute(
        select(Account)
        .where(Account.user_id == user_id)
        .order_by(Account.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def find_or_create_account(db: AsyncSession, user_id: uuid.UUID, company_name: str, **kwargs) -> Account:
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id, func.lower(Account.company_name) == company_name.lower().strip()
        )
    )
    account = result.scalar_one_or_none()
    if account:
        return account
    account = Account(user_id=user_id, company_name=company_name.strip(), **kwargs)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


# ---------------------------------------------------------------- Signals
async def create_signal(db: AsyncSession, **kwargs) -> Signal:
    signal = Signal(**kwargs)
    db.add(signal)
    await db.commit()
    await db.refresh(signal)
    return signal


async def list_signals(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    account_id: uuid.UUID | None = None,
    source: str | None = None,
    signal_type: str | None = None,
    tier: int | None = None,
    since: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Signal]:
    stmt = select(Signal).join(Account, Signal.account_id == Account.id).where(Account.user_id == user_id)
    if account_id:
        stmt = stmt.where(Signal.account_id == account_id)
    if source:
        stmt = stmt.where(Signal.source == source)
    if signal_type:
        stmt = stmt.where(Signal.signal_type == signal_type)
    if tier is not None:
        stmt = stmt.where(Account.tier == tier)
    if since:
        stmt = stmt.where(Signal.detected_at >= since)
    stmt = stmt.options(selectinload(Signal.account)).order_by(Signal.detected_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def record_signal_score(db: AsyncSession, **kwargs) -> SignalScore:
    score_row = SignalScore(**kwargs)
    db.add(score_row)
    await db.commit()
    await db.refresh(score_row)
    return score_row


async def count_signals_since(db: AsyncSession, user_id: uuid.UUID, since: datetime) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Signal)
        .where(Signal.user_id == user_id, Signal.detected_at >= since)
    )
    return int(result.scalar_one())


# ---------------------------------------------------------------- Misc helpers
async def count(db: AsyncSession, model, **filters) -> int:
    stmt = select(func.count()).select_from(model)
    for key, value in filters.items():
        if value is not None:
            stmt = stmt.where(getattr(model, key) == value)
    result = await db.execute(stmt)
    return int(result.scalar_one())


def iso_weeks_ago(weeks: int) -> datetime:
    return datetime.utcnow() - timedelta(weeks=weeks)
