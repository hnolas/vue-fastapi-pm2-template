import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Participant Management Interface & Fitbit Data Integration System"
    
    # Database
    POSTGRES_SERVER: str = os.getenv("PGHOST", "localhost")
    POSTGRES_USER: str = os.getenv("PGUSER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("PGDATABASE", "app")
    POSTGRES_PORT: str = os.getenv("PGPORT", "5432")
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data["POSTGRES_USER"],
            password=values.data["POSTGRES_PASSWORD"],
            host=values.data["POSTGRES_SERVER"],
            port=int(values.data["POSTGRES_PORT"]),
            path=f"/{values.data['POSTGRES_DB']}"  # important to have leading /
        )


    # JWT
    ALGORITHM: str = "HS256"
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    # External base URL for callbacks (e.g., Twilio status callbacks)
    EXTERNAL_BASE_URL: str = os.getenv("EXTERNAL_BASE_URL", "http://localhost:8000")
    
    # Fitbit
    FITBIT_CLIENT_ID: str = os.getenv("FITBIT_CLIENT_ID", "")
    FITBIT_CLIENT_SECRET: str = os.getenv("FITBIT_CLIENT_SECRET", "")
    
    # Dropbox (for Fitbit data export)
    DROPBOX_ACCESS_TOKEN: str = os.getenv("DROPBOX_ACCESS_TOKEN", "")
    FITBIT_DATA_EXPORT_PATH: str = os.getenv("FITBIT_DATA_EXPORT_PATH", "/fitbit_data")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
