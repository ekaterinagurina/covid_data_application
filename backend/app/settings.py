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

    @property
    def uri(self):
        return (
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

class RedisSettings(ConfiguredBaseSettings):
    REDIS_HOST: str = Field(..., description="Redis host address")
    REDIS_PORT: int = Field(..., description="Redis port")
    REDIS_CACHE_TTL: int = Field(..., description="Redis cache time-to-live in seconds")


class Settings(ConfiguredBaseSettings):
    SECRET_KEY: str = Field(..., description="JWT Secret Key")
    ALLOW_ORIGINS: List[str] = Field(..., description="List of allowed origins for CORS")
    NATS_URL: str = Field(..., description="NATS server URL")


settings = Settings()
database_settings = DatabaseSettings()
redis_settings = RedisSettings()