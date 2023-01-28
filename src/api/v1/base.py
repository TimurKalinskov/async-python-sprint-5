from fastapi import APIRouter

from .urls_shorts import router
from .inspect import router as inspect_router

# Объект router, в котором регистрируем обработчики
api_router = APIRouter()
api_router.include_router(router, prefix='/url_shorts', tags=['short urls'])
api_router.include_router(inspect_router, prefix='/inspect', tags=['inspect'])
