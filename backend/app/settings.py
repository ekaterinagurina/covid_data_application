from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "covid_database"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_CACHE_TTL: int = 300

    class Config:
        env_file = ".env"
