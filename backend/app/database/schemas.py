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
    ab_enabled: bool | None = None


class CampaignOut(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    tier_filters: dict[str, Any] | None = None
    channels: dict[str, Any] | None = None
    cadence: dict[str, Any] | None = None
    ab_enabled: bool = False
    ab_won: str | None = None
    last_run_at: datetime | None = None
    run_log: str | None = None
    created_at: datetime
    updated_at: datetime


class CampaignDetailOut(CampaignOut):
    account_count: int = 0
    sent_count: int = 0
    reply_count: int = 0
    open_count: int = 0
    click_count: int = 0
    last_run_at: datetime | None = None
    run_log: str | None = None


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


class CampaignEmailsIn(BaseModel):
    emails: list[str] = Field(min_length=1)

    @field_validator("emails")
    @classmethod
    def validate_emails(cls, v: list[str]) -> list[str]:
        cleaned = [e.strip() for e in v if e and "@" in e]
        if not cleaned:
            raise ValueError("No valid email addresses provided")
        return cleaned[:500]


class CampaignRunOut(BaseModel):
    campaign_id: uuid.UUID
    queued: int
    message: str


class CampaignAccountOut(ORMModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    account_id: uuid.UUID
    contact_email: str | None = None
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
    variant: str = "A"
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
    meta: dict[str, Any] | None = Field(default=None, validation_alias="meta", serialization_alias="metadata")


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


# ---------------------------------------------------------------- Outcomes
class OutcomesOut(BaseModel):
    pipeline_value: float
    pipeline_by_tier: list[MetricPoint]
    accounts_scored: int
    signals_detected: int
    deals_estimate: int
    time_saved_hours: float
    labor_value: float
    reply_rate: float
    open_rate: float
    click_rate: float
    industry_reply_rate: float
    engagement_lift_pct: float
    cost_per_meeting: float
    monthly_forecast: float
    forecast_growth_pct: float
    note: str = ""


class InsightItem(BaseModel):
    label: str
    detail: str
    value: str


class LearningOut(BaseModel):
    top_attributes: list[InsightItem]
    signal_performance: list[InsightItem]
    email_tactics: list[InsightItem]
    recommendations: list[InsightItem]


# ---------------------------------------------------------------- Replies
class EmailReplyOut(BaseModel):
    id: uuid.UUID
    from_email: str
    subject: str | None = None
    body: str
    classification: str
    confidence: float | None = None
    summary: str | None = None
    suggested_reply: str | None = None
    auto_reply_sent: bool
    status: str
    created_at: datetime
    company_name: str | None = None
    original_subject: str | None = None


# ---------------------------------------------------------------- Intelligence
class AccountMessageOut(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    campaign_name: str | None = None
    subject: str
    to_email: str
    status: str
    sequence_step: int
    sent_at: datetime | None = None
    opened_at: datetime | None = None
    clicked_at: datetime | None = None
    replied_at: datetime | None = None
    created_at: datetime


class AccountIntelligenceOut(BaseModel):
    account_id: uuid.UUID
    contact_email: str | None = None
    emails_sent: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    emails_replied: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0
    high_intent_signals: int = 0
    medium_intent_signals: int = 0
    low_intent_signals: int = 0
    campaigns: list[AccountMessageOut] = []
    best_message: AccountMessageOut | None = None


# ---------------------------------------------------------------- Timeline
class TimelineItemOut(BaseModel):
    event_type: str
    label: str
    occurred_at: datetime
    account_name: str | None = None
    subject: str | None = None
    to_email: str | None = None
    detail: str | None = None


class CampaignTimelineOut(BaseModel):
    campaign_id: uuid.UUID
    items: list[TimelineItemOut]


# ---------------------------------------------------------------- Digest
class DigestPreviewOut(BaseModel):
    subject: str
    text: str


class DigestSendOut(BaseModel):
    ok: bool
    message: str


# ---------------------------------------------------------------- A/B testing
class AbVariantStats(BaseModel):
    variant: str
    sent: int = 0
    opened: int = 0
    clicked: int = 0
    replied: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0


class AbTestOut(BaseModel):
    campaign_id: uuid.UUID
    campaign_name: str
    ab_enabled: bool
    ab_won: str | None = None
    variants: list[AbVariantStats] = []
    winner: AbVariantStats | None = None
    note: str = ""
