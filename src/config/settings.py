import os
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn, Field


BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG_ENV = os.path.join(BASE_DIR, 'config', '.env.db')


class Settings(BaseSettings):
    pg_dsn: PostgresDsn = Field(..., env='DB_DSN')
    pg_name: str = Field(..., env='DB_NAME')
    pg_user: str = Field(..., env='DB_USER')
    pg_pwd: str = Field(..., env='DB_PWD')
    pg_host: str = Field(..., env='DB_HOST')
    pg_port: int = Field(..., env='DB_PORT')

    class Config:
        env_file = DEBUG_ENV


class AppSettings(BaseSettings):
    debug: bool = Field(..., env='APP_DEBUG')
    port: int = Field(..., env='APP_PORT')
    host: str = Field(..., env='APP_HOST')

    class Config:
        env_file = DEBUG_ENV


DB_SETTINGS = Settings()
APP_SETTINGS = AppSettings()
