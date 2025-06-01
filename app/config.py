import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    api_title: str = "Logistics Management API"
    api_version: str = "1.0.0"
    api_description: str = "API for managing logistics operations"

    default_page_size: int = 10
    max_page_size: int = 100

    log_level: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
