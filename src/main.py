import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import app_settings
from core.logger import LOGGING
from api.v1 import base as v1_base


app = FastAPI(
    title=app_settings.app_title,
    docs_url="/api/docs",
    openapi_url="/api/docs.json",
    default_response_class=ORJSONResponse,
)

app.include_router(v1_base.api_router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
        log_config=LOGGING
    )
