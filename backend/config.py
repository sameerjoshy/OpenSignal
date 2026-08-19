from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    environment: str = "development"
    log_level: str = "debug"

    # Database / Cache
    database_url: str = "postgresql+asyncpg://opensignal:opensignal@localhost:5432/opensignal"
    redis_url: str = "redis://localhost:6379/0"

    # Security
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    encryption_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Supabase Auth (user management)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # DeepSeek AI (scoring + personalized email generation)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model_id: str = "deepseek-chat"

    # Global service keys (fallbacks; per-user keys are stored encrypted)
    apollo_api_key: str = ""
    hunter_api_key: str = ""
    mailgun_api_key: str = ""
    mailgun_domain: str = ""
    sendgrid_api_key: str = ""
    sendgrid_webhook_verification_key: str = ""
    newsapi_key: str = ""
    hubspot_api_key: str = ""
    salesforce_client_id: str = ""
    salesforce_client_secret: str = ""
    salesforce_username: str = ""
    salesforce_password: str = ""
    salesforce_instance_url: str = ""

    # Google Analytics 4
    ga4_property_id: str = ""
    ga4_service_account_json: str = ""

    # Monitoring
    sentry_dsn: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def guard_insecure(self) -> None:
        """Fail fast in production when security-critical settings are defaults/missing."""
        if not self.is_production:
            return
        if not self.jwt_secret or self.jwt_secret == "change-me":
            raise RuntimeError("JWT_SECRET must be set to a strong random value in production")
        if not self.encryption_key:
            raise RuntimeError("ENCRYPTION_KEY must be set in production (used for credential encryption)")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
