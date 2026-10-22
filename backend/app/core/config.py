import os
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LifeLine - Emergency Blood & Rare Donor Network"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Security & JWT
    SECRET_KEY: str = "lifeline-secret-super-secure-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    # Database: AWS RDS PostgreSQL or Local Postgres
    # Defaults to SQLite if PostgreSQL connection string is not provided
    DATABASE_URL: str = "sqlite:///./lifeline.db"

    # AWS Free Tier Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # AWS S3 (Donor certificates & hospital verification docs)
    AWS_S3_BUCKET_NAME: str = "lifeline-medical-documents"
    AWS_S3_SSE_ALGORITHM: str = "AES256"  # SSE-S3 Server-Side Encryption
    MAX_FILE_SIZE_MB: int = 10

    # AWS SNS (Urgent SMS notifications to matching donors)
    AWS_SNS_TOPIC_ARN: str = ""
    SMS_SENDER_ID: str = "LifeLine"

    # AWS SES (Emergency email alerts to regional hospitals and blood banks)
    AWS_SES_SENDER_EMAIL: str = "alerts@lifeline-emergency.org"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1",
        "http://localhost",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
