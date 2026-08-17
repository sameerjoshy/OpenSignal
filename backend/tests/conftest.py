import base64
import os
import uuid

# Set test env BEFORE importing any app modules (settings is cached at import).
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(b"0" * 32).decode()
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_ANON_KEY"] = ""
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""
os.environ["AWS_ACCESS_KEY_ID"] = ""
os.environ["AWS_SECRET_ACCESS_KEY"] = ""
os.environ["REDIS_URL"] = ""
os.environ["CORS_ORIGINS"] = "http://testserver"

# Clear any globally-set service keys so tests never hit external APIs
for _key in [
    "APOLLO_API_KEY",
    "HUNTER_API_KEY",
    "NEWSAPI_KEY",
    "MAILGUN_API_KEY",
    "MAILGUN_DOMAIN",
    "SENDGRID_API_KEY",
    "HUBSPOT_API_KEY",
    "SALESFORCE_CLIENT_ID",
    "SALESFORCE_CLIENT_SECRET",
    "SALESFORCE_USERNAME",
    "SALESFORCE_PASSWORD",
    "GA4_PROPERTY_ID",
    "GA4_SERVICE_ACCOUNT_JSON",
]:
    os.environ[_key] = ""

import httpx  # noqa: E402
import pytest  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.database.models import Base  # noqa: E402
from app.database.session import AsyncSessionLocal, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    from main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def user_token(client) -> str:
    email = f"sarah{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "full_name": "Sarah Founder"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]
