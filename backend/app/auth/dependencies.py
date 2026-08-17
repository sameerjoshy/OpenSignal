import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token, decode_supabase_token
from app.database import crud
from app.database.models import User
from app.database.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials

    # Try OpenSignal-issued JWT first.
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            user = await crud.get_user(db, uuid.UUID(user_id))
            if user and user.is_active:
                return user
    except Exception:  # noqa: BLE001
        pass

    # Fall back to a Supabase Auth access token.
    try:
        payload = decode_supabase_token(token)
        supabase_id = payload.get("sub")
        user = await crud.get_user_by_supabase_id(db, supabase_id)
        if user is None:
            email = payload.get("email")
            if email:
                user = await crud.upsert_supabase_user(db, email, supabase_id)
        if user and user.is_active:
            return user
    except Exception:  # noqa: BLE001
        pass

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
