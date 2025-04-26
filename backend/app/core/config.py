import os
from dotenv import load_dotenv

# 🛠 Load .env file first, from 3 levels up
dotenv_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..", ".env")
)
load_dotenv(dotenv_path)

print("✅ .env loaded from:", dotenv_path)
print("✅ PGUSER:", os.getenv("PGUSER"))
print("✅ PGPASSWORD:", os.getenv("PGPASSWORD"))

# Now continue imports
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, AnyHttpUrl, field_validator, ValidationInfo


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Participant Management Interface"

    # 🛠 Now these env vars will be read properly
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
            path=f"/{values.data['POSTGRES_DB']}",
        )

    ALGORITHM: str = "HS256"

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    EXTERNAL_BASE_URL: str = os.getenv("EXTERNAL_BASE_URL", "http://localhost:8000")

    FITBIT_CLIENT_ID: str = os.getenv("FITBIT_CLIENT_ID", "")
    FITBIT_CLIENT_SECRET: str = os.getenv("FITBIT_CLIENT_SECRET", "")

    DROPBOX_ACCESS_TOKEN: str = os.getenv("DROPBOX_ACCESS_TOKEN", "")
    FITBIT_DATA_EXPORT_PATH: str = os.getenv("FITBIT_DATA_EXPORT_PATH", "/fitbit_data")

    class Config:
        case_sensitive = True

# 🛠 Create instance AFTER loading .env
settings = Settings()
