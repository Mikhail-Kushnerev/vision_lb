from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from uvicorn import run

from api.v1.graph import graph_router

app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.include_router(graph_router)


if __name__ == '__main__':

    if True:
        run(
            app,
            host='0.0.0.0',
            port=8100
        )
