from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "FinanceCalculator API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str = ""
    database_name: str = "financecalculator"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    allowed_hosts: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    rate_limit_per_minute: int = 60
    rate_limit_per_minute_public: int = 120

    log_level: str = "DEBUG"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | {name}:{function}:{line} | {message}"

    upload_max_size_mb: int = 50
    default_locale: str = "en-US"
    default_timezone: str = "UTC"

    redis_url: str = ""
    cache_ttl_default: int = 300
    cache_ttl_long: int = 3600
    cache_prefix: str = "fc:"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@financecalculator.com"
    smtp_from_name: str = "FinanceCalculator"
    smtp_use_tls: bool = True

    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    backup_dir: str = "backups"
    backup_retention_days: int = 30
    pg_dump_path: str = "pg_dump"

    scheduler_enabled: bool = True
    scheduler_check_interval_seconds: int = 60

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"


settings = Settings()
