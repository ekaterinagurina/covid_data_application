from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class ConfiguredBaseSettings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


class DatabaseSettings(ConfiguredBaseSettings):
    DB_HOST: str = Field(..., description="Database host address")
    DB_PORT: str = Field(..., description="Database port")
    DB_NAME: str = Field(..., description="Database name")
    DB_USER: str = Field(..., description="Database username")
    DB_PASSWORD: str = Field(..., description="Database password")


class RedisSettings(ConfiguredBaseSettings):
    REDIS_HOST: str = Field(..., description="Redis host address")
    REDIS_PORT: int = Field(..., description="Redis port")
    REDIS_CACHE_TTL: int = Field(..., description="Redis cache time-to-live in seconds")


class Settings(ConfiguredBaseSettings):
    SECRET_KEY: str = Field(..., description="JWT Secret Key")
    ALLOW_ORIGINS: List[str] = Field(..., description="List of allowed origins for CORS")


settings = Settings()
database_settings = DatabaseSettings()
redis_settings = RedisSettings()