import os
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn, Field


BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG_ENV = os.path.join(BASE_DIR, 'config', '.env.db')


class Settings(BaseSettings):
    pg_dsn: PostgresDsn = Field(..., env='POSTGRES_DSN')
    pg_name: str = Field(..., env='POSTGRES_DB')
    pg_user: str = Field(..., env='POSTGRES_USER')
    pg_pwd: str = Field(..., env='POSTGRES_PASSWORD')
    pg_host: str = Field(..., env='POSTGRES_HOST')
    pg_port: int = Field(..., env='POSTGRES_PORT')

    class Config:
        env_file = DEBUG_ENV


DB_SETTINGS = Settings()
