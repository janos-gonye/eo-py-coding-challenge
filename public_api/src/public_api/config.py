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
    log_file: str


settings = Settings()
