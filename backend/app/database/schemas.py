import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Auth
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ExchangeRequest(BaseModel):
    access_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(ORMModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    plan: str
    is_active: bool
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ---------------------------------------------------------------- Services
class ServiceCredentialIn(BaseModel):
    service: str
    api_key: str = Field(min_length=1)
    config: dict[str, Any] | None = None


class ServiceCredentialOut(ORMModel):
    id: uuid.UUID
    service: str
    is_active: bool
    validated_at: datetime | None = None
    config: dict[str, Any] | None = None
    created_at: datetime


class ServiceTestOut(BaseModel):
    service: str
    ok: bool
    message: str
    quota: dict[str, Any] | None = None


# ---------------------------------------------------------------- Accounts
class AccountIn(BaseModel):
    company_name: str
    domain: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    revenue: float | None = None
    location: str | None = None
    website: str | None = None


class AccountUpdate(BaseModel):
    industry: str | None = None
    employee_count: int | None = None
    revenue: float | None = None
    location: str | None = None
    website: str | None = None


class AccountOut(ORMModel):
    id: uuid.UUID
    company_name: str
    domain: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    revenue: float | None = None
    location: str | None = None
    website: str | None = None
    score: float | None = None
    tier: int | None = None
    score_rationale: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- Signals
class SignalIn(BaseModel):
    account_id: uuid.UUID
    source: str = "manual"
    signal_type: str
    title: str
    description: str | None = None
    url: str | None = None


class SignalOut(ORMModel):
    id: uuid.UUID
    account_id: uuid.UUID
    source: str
    signal_type: str
    title: str
    description: str | None = None
    url: str | None = None
    detected_at: datetime
    created_at: datetime


class SignalWithAccountOut(SignalOut):
    account_name: str | None = None
    account_tier: int | None = None
    account_score: float | None = None


class ScoreOut(ORMModel):
    id: uuid.UUID
    account_id: uuid.UUID
    score: float
    tier: int
    model_used: str | None = None
    rationale: str | None = None
    scored_at: datetime


# ---------------------------------------------------------------- Campaigns
class CampaignIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    tier_filters: dict[str, Any] | None = None
    channels: dict[str, Any] | None = None
    cadence: dict[str, Any] | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: Literal["draft", "active", "paused", "completed", "archived"] | None = None
    tier_filters: dict[str, Any] | None = None
    channels: dict[str, Any] | None = None
    cadence: dict[str, Any] | None = None


class CampaignOut(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    tier_filters: dict[str, Any] | None = None
    channels: dict[str, Any] | None = None
    cadence: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class CampaignDetailOut(CampaignOut):
    account_count: int = 0
    sent_count: int = 0
    reply_count: int = 0
    open_count: int = 0
    click_count: int = 0


class CampaignImportIn(BaseModel):
    companies: list[str] = Field(min_length=1)
    tier_filters: dict[str, Any] | None = None
    channels: dict[str, Any] | None = None
    cadence: dict[str, Any] | None = None

    @field_validator("companies")
    @classmethod
    def validate_companies(cls, v: list[str]) -> list[str]:
        cleaned = [c.strip() for c in v if c and c.strip()]
        if not cleaned:
            raise ValueError("No companies provided")
        return cleaned[:500]


class CampaignRunOut(BaseModel):
    campaign_id: uuid.UUID
    queued: int
    message: str


class CampaignAccountOut(ORMModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    account_id: uuid.UUID
    status: str
    tier: int | None = None
    score: float | None = None
    error: str | None = None
    created_at: datetime
    account: AccountOut | None = None


# ---------------------------------------------------------------- Email
class EmailTemplateIn(BaseModel):
    name: str
    subject: str
    body: str
    sequence_step: int = 1
    is_default: bool = False


class EmailTemplateOut(ORMModel):
    id: uuid.UUID
    name: str
    subject: str
    body: str
    sequence_step: int
    is_default: bool
    created_at: datetime


class EmailMessageOut(ORMModel):
    id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    subject: str
    body_text: str
    status: str
    from_email: str | None = None
    to_email: str
    provider: str | None = None
    sequence_step: int
    sent_at: datetime | None = None
    opened_at: datetime | None = None
    clicked_at: datetime | None = None
    replied_at: datetime | None = None
    created_at: datetime


class EmailEventOut(ORMModel):
    id: uuid.UUID
    email_message_id: uuid.UUID
    event_type: str
    occurred_at: datetime
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------- CRM
class CrmSyncRequest(BaseModel):
    campaign_id: uuid.UUID
    service: Literal["hubspot", "salesforce"]


class CrmSyncOut(ORMModel):
    id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    service: str
    status: str
    object_type: str | None = None
    external_id: str | None = None
    error_message: str | None = None
    synced_at: datetime | None = None
    created_at: datetime


# ---------------------------------------------------------------- Analytics
class MetricPoint(BaseModel):
    label: str
    value: float


class FunnelStep(BaseModel):
    label: str
    value: int


class AnalyticsOut(BaseModel):
    total_signals: int
    total_accounts: int
    total_campaigns: int
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    emails_replied: int
    active_campaigns: int
    signals_this_week: int
    top_sources: list[MetricPoint]
    signals_by_tier: list[MetricPoint]
    funnel: list[FunnelStep]
    weekly_activity: list[MetricPoint]
