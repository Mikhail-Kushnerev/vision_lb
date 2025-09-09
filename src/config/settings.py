"""Модуль настроек."""

import os
from pathlib import Path
from typing import List

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


class HTTPClientSettings(BaseSettings):
    """Настройки для оптимизированного HTTP клиента."""
    
    # Connection pooling
    connection_limit: int = Field(100, env='HTTP_CONNECTION_LIMIT')
    connection_limit_per_host: int = Field(30, env='HTTP_CONNECTION_LIMIT_PER_HOST')
    
    # DNS settings
    dns_cache_ttl: int = Field(300, env='HTTP_DNS_CACHE_TTL')
    use_dns_cache: bool = Field(True, env='HTTP_USE_DNS_CACHE')
    
    # Keep-alive settings
    keepalive_timeout: int = Field(60, env='HTTP_KEEPALIVE_TIMEOUT')
    enable_cleanup_closed: bool = Field(True, env='HTTP_ENABLE_CLEANUP_CLOSED')
    
    # Performance settings  
    tcp_nodelay: bool = Field(True, env='HTTP_TCP_NODELAY')
    
    # Timeout settings
    total_timeout: int = Field(30, env='HTTP_TOTAL_TIMEOUT')
    connect_timeout: int = Field(5, env='HTTP_CONNECT_TIMEOUT')
    sock_connect_timeout: int = Field(5, env='HTTP_SOCK_CONNECT_TIMEOUT')
    sock_read_timeout: int = Field(10, env='HTTP_SOCK_READ_TIMEOUT')
    
    # Event endpoints
    event_endpoints: List[str] = Field(
        default=[
            "http://analytics-service:8080/events",
            "http://notification-service:8081/events",
        ],
        env='HTTP_EVENT_ENDPOINTS'
    )
    
    class Config:
        env_file = DEBUG_ENV


DB_SETTINGS = Settings()
APP_SETTINGS = AppSettings()
HTTP_CLIENT_SETTINGS = HTTPClientSettings()
