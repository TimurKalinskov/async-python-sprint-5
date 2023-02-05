import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette_validation_uploadfile import ValidateUploadFileMiddleware

from core.config import app_settings
from core.logger import LOGGING
from api.v1 import api_router as v1_router


app = FastAPI(
    title=app_settings.app_title,
    docs_url="/api/docs",
    openapi_url="/api/docs.json",
    default_response_class=ORJSONResponse,
)

app.include_router(v1_router, prefix='/api/v1')

app.add_middleware(
        ValidateUploadFileMiddleware,
        app_path=app.url_path_for('upload_file'),
        max_size=app_settings.max_size_file,
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
        log_config=LOGGING
    )
