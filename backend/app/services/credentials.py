"""Resolve credentials for a service: per-user (AES-256 encrypted) with global env fallback."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.security.encryption import decrypt_value
from app.services.base import ServiceNotConfigured
from config import settings


@dataclass
class ServiceCredentials:
    api_key: str = ""
    config: dict | None = None
    source: str = "env"  # "env" | "user"


async def resolve_credentials(db: AsyncSession, user_id, service: str) -> ServiceCredentials:
    """Prefer the user's stored (encrypted) key, falling back to env-configured globals."""
    cred = await crud.get_credential(db, user_id, service)
    if cred:
        try:
            key = decrypt_value(cred.encrypted_key)
            return ServiceCredentials(api_key=key, config=cred.config or {}, source="user")
        except ValueError:
            pass  # fall through to env default

    from app.services.registry import SERVICE_BY_ID

    meta = SERVICE_BY_ID.get(service)
    env_key = getattr(settings, meta.env_api_key, "") if meta else ""
    return ServiceCredentials(api_key=env_key, config={}, source="env")


def require_key(credentials: ServiceCredentials, service: str) -> str:
    if not credentials.api_key:
        raise ServiceNotConfigured(service)
    return credentials.api_key
