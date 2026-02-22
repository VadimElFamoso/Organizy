from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: Literal["dev", "prod"] = "dev"

    @property
    def debug(self) -> bool:
        """Return True if in dev environment."""
        return self.environment == "dev"

    # Database
    database_url: str = "postgresql+asyncpg://launchpad:launchpad@localhost:5432/launchpad"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_starter_monthly: str = ""
    stripe_price_id_starter_yearly: str = ""
    stripe_price_id_pro_monthly: str = ""
    stripe_price_id_pro_yearly: str = ""
    stripe_price_id_unlimited_monthly: str = ""
    stripe_price_id_unlimited_yearly: str = ""

    # Frontend
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Ensure JWT secret is strong enough."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate that production has all required secrets properly configured."""
        if self.environment != "prod":
            return self

        errors = []

        # JWT must not be the default
        if self.jwt_secret_key == "change-me-in-production":
            errors.append("JWT_SECRET_KEY must be changed from default in production")

        # Google OAuth required in production
        if not self.google_client_id:
            errors.append("GOOGLE_CLIENT_ID is required in production")
        if not self.google_client_secret:
            errors.append("GOOGLE_CLIENT_SECRET is required in production")

        # Stripe required in production
        if not self.stripe_secret_key:
            errors.append("STRIPE_SECRET_KEY is required in production")
        if not self.stripe_webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is required in production")

        # Frontend URL must be HTTPS in production
        if not self.frontend_url.startswith("https://"):
            errors.append("FRONTEND_URL must use HTTPS in production")

        if errors:
            raise ValueError(f"Production configuration errors: {'; '.join(errors)}")

        return self


settings = Settings()
