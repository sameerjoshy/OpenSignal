"""User management provider.

Prioritizes Supabase Auth for user management. When Supabase is not
configured (e.g. local development or tests) it falls back to local
email/password accounts stored in the `users` table.
"""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_supabase_token
from app.database import crud
from app.database.models import User
from config import settings


class AuthError(Exception):
    pass


def supabase_enabled() -> bool:
    return bool(settings.supabase_url and settings.supabase_anon_key)


def _headers(role: str) -> dict[str, str]:
    key = settings.supabase_service_role_key if role == "service" else settings.supabase_anon_key
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


async def _supabase_signup(email: str, password: str, full_name: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{settings.supabase_url}/auth/v1/signup",
            headers=_headers("anon"),
            json={"email": email, "password": password, "data": {"full_name": full_name}},
        )
        if resp.status_code >= 400:
            raise AuthError("SIGNUP_FAILED")
        data = resp.json()
        if "id" not in data:
            raise AuthError("SIGNUP_FAILED")
        return data


async def _supabase_sign_in(email: str, password: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{settings.supabase_url}/auth/v1/token?grant_type=password",
            headers=_headers("anon"),
            json={"email": email, "password": password},
        )
        if resp.status_code >= 400:
            raise AuthError("INVALID_CREDENTIALS")
        return resp.json()


async def _supabase_get_user(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"apikey": settings.supabase_anon_key, "Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code >= 400:
            raise AuthError("INVALID_TOKEN")
        return resp.json()


async def signup(db: AsyncSession, email: str, password: str, full_name: str) -> User:
    if await crud.get_user_by_email(db, email):
        raise AuthError("EMAIL_EXISTS")

    if supabase_enabled():
        data = await _supabase_signup(email, password, full_name)
        return await crud.upsert_supabase_user(db, email, data["id"], full_name)

    user = User(email=email, full_name=full_name)
    user.set_password(password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    if supabase_enabled():
        data = await _supabase_sign_in(email, password)
        su = data.get("user") or {}
        full_name = (su.get("user_metadata") or {}).get("full_name") or su.get("email")
        user = await crud.upsert_supabase_user(db, email, su.get("id") or "", full_name)
    else:
        user = await crud.get_user_by_email(db, email)
        if not user or not user.password_hash or not user.verify_password(password):
            raise AuthError("INVALID_CREDENTIALS")

    if not user.is_active:
        raise AuthError("ACCOUNT_DISABLED")
    return user


async def exchange_supabase_token(db: AsyncSession, access_token: str) -> User:
    try:
        payload = decode_supabase_token(access_token)
    except Exception as exc:  # noqa: BLE001
        raise AuthError("INVALID_TOKEN") from exc

    supabase_id = payload.get("sub")
    email = payload.get("email")

    if not email:
        profile = await _supabase_get_user(access_token)
        email = profile.get("email")
        supabase_id = profile.get("id") or supabase_id

    if not email or not supabase_id:
        raise AuthError("INVALID_TOKEN")

    full_name = None
    metadata = payload.get("user_metadata")
    if isinstance(metadata, dict):
        full_name = metadata.get("full_name")
    return await crud.upsert_supabase_user(db, email, supabase_id, full_name)


async def request_password_reset(email: str) -> None:
    if supabase_enabled():
        async with httpx.AsyncClient(timeout=20) as client:
            await client.post(
                f"{settings.supabase_url}/auth/v1/recover",
                headers=_headers("anon"),
                json={"email": email},
            )
