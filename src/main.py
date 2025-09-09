"""Модуль, запускающий `uvicorn` сервер для FastApi-приложения."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from uvicorn import run

from api.routers import main_router
from config.settings import APP_SETTINGS
from services.http_client import cleanup_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    yield
    # Shutdown
    await cleanup_http_client()


app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.include_router(main_router, prefix='/track')


if __name__ == '__main__':

    if APP_SETTINGS.debug:
        run(
            app,
            host=APP_SETTINGS.host,
            port=APP_SETTINGS.port
        )
