from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "insurance"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: str = "*"
    CONTRACT_TEMPLATE_PATH: str = "app/templates/insurance_blank.docx"
    INSURER_FULL_NAME: str = "Урста Всеволод Олегович"
    AUTH_LOG_DIR: str = "logs"
    AUTH_LOG_FILENAME: str = "auth.log"
    AUTH_LOG_MAX_BYTES: int = 5 * 1024 * 1024
    AUTH_LOG_BACKUP_COUNT: int = 5
    DOCUMENT_LOG_DIR: str = "logs"
    DOCUMENT_LOG_FILENAME: str = "documents.log"
    DOCUMENT_LOG_MAX_BYTES: int = 5 * 1024 * 1024
    DOCUMENT_LOG_BACKUP_COUNT: int = 5

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
