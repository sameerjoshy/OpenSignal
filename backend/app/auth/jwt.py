import uuid
from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from config import settings

TOKEN_AUDIENCE = "opensignal"
SUPABASE_AUDIENCE = "authenticated"


def create_access_token(user_id: uuid.UUID, *, extra: dict | None = None) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict = {
        "sub": str(user_id),
        "aud": TOKEN_AUDIENCE,
        "iat": now,
        "exp": now + expires_delta,
        "iss": "opensignal",
    }
    if extra:
        payload.update(extra)
    token = pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str) -> dict:
    """Validate an OpenSignal-issued JWT."""
    return pyjwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        audience=TOKEN_AUDIENCE,
    )


def decode_supabase_token(token: str) -> dict:
    """Validate a Supabase Auth access token (HS256, audience 'authenticated')."""
    if not settings.supabase_jwt_secret:
        raise ValueError("SUPABASE_JWT_SECRET is not configured")
    return pyjwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience=SUPABASE_AUDIENCE,
    )