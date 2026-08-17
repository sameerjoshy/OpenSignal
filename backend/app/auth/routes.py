from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import provider
from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.auth.provider import AuthError
from app.database import schemas
from app.database.models import User
from app.database.session import get_db

router = APIRouter()


def _token_response(user: User) -> schemas.TokenOut:
    token, expires_in = create_access_token(user.id)
    return schemas.TokenOut(access_token=token, expires_in=expires_in, user=schemas.UserOut.model_validate(user))


@router.post("/signup", response_model=schemas.TokenOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: schemas.SignupRequest, db: AsyncSession = Depends(get_db)) -> schemas.TokenOut:
    try:
        user = await provider.signup(db, payload.email, payload.password, payload.full_name)
    except AuthError as exc:
        code = str(exc)
        detail = {
            "EMAIL_EXISTS": "An account with this email already exists.",
            "SIGNUP_FAILED": "Signup failed. Please try again.",
        }.get(code, str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    return _token_response(user)


@router.post("/login", response_model=schemas.TokenOut)
async def login(payload: schemas.LoginRequest, db: AsyncSession = Depends(get_db)) -> schemas.TokenOut:
    try:
        user = await provider.authenticate(db, payload.email, payload.password)
    except AuthError as exc:
        detail = {
            "INVALID_CREDENTIALS": "Incorrect email or password.",
            "ACCOUNT_DISABLED": "This account has been disabled.",
        }.get(str(exc), str(exc))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail) from exc
    return _token_response(user)


@router.post("/exchange", response_model=schemas.TokenOut)
async def exchange(payload: schemas.ExchangeRequest, db: AsyncSession = Depends(get_db)) -> schemas.TokenOut:
    """Exchange a Supabase Auth access token for an OpenSignal JWT."""
    try:
        user = await provider.exchange_supabase_token(db, payload.access_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return _token_response(user)


@router.get("/me", response_model=schemas.UserOut)
async def me(current_user: User = Depends(get_current_user)) -> schemas.UserOut:
    return schemas.UserOut.model_validate(current_user)


@router.post("/forgot-password")
async def forgot_password(payload: schemas.ForgotPasswordRequest) -> dict[str, str]:
    await provider.request_password_reset(payload.email)
    return {"message": "If an account exists, a password reset link has been sent."}
