from fastapi import APIRouter

from .inspect import router as inspect_router
from .auth import router as auth_router
from .files import router as file_router


# Объект router, в котором регистрируем обработчики
api_router = APIRouter()
api_router.include_router(inspect_router, prefix='/inspect', tags=['inspect'])
api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
api_router.include_router(file_router, prefix='/files', tags=['files'])
