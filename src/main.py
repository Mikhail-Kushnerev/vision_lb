"""Модуль, запускающий `uvicorn` сервер для FastApi-приложения."""

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from uvicorn import run

from api.routers import main_router
from config.settings import APP_SETTINGS

app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.include_router(main_router, prefix='/track')


if __name__ == '__main__':

    if APP_SETTINGS.debug:
        run(
            app,
            host=APP_SETTINGS.host,
            port=APP_SETTINGS.port
        )
