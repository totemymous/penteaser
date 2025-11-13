"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://xss_user:password@localhost/xss_assistant"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Security
    secret_key: str = "change-this-secret-key"
    api_key_salt: str = "change-this-salt"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Browser
    browser_type: str = "playwright"  # or "selenium"
    headful_mode: bool = True
    browser_timeout: int = 30000  # milliseconds

    # Storage
    session_recordings_path: str = "/tmp/xss-assistant/recordings"
    encryption_key: str = "change-this-encryption-key"

    # Application
    app_name: str = "XSS Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # Security & Compliance (Optional for development/lab environments)
    require_consent: bool = True  # Set to False for lab/development use
    auto_approve_sessions: bool = False  # Set to True to bypass human approval
    minimal_logging: bool = False  # Set to True for reduced audit logging

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
