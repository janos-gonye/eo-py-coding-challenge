"""
Configuration module for the Public API application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    cors_allow_origins: list[str]
    cors_allow_methods: list[str]
    cors_allow_headers: list[str]
    redis_url: str
    log_file: str
    db_path: str
    api_key_virustotal: str
    virustotal_endpoint: str


settings = Settings()
