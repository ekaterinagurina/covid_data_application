from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class DatabaseSettings(BaseSettings):
    DB_HOST: str = Field(default="localhost", description="Database host address")
    DB_PORT: str = Field(default="5432", description="Database port")
    DB_NAME: str = Field(default="covid_database", description="Database name")
    DB_USER: str = Field(default="postgres", description="Database username")
    DB_PASSWORD: str = Field(default="password", description="Database password")

class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(default="redis", description="Redis host address")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_CACHE_TTL: int = Field(default=300, description="Redis cache time-to-live in seconds")

class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ALLOW_ORIGINS: List[str] = Field(default=["http://localhost:8080"], description="List of allowed origins for CORS")

    class Config:
        env_file = ".env"
