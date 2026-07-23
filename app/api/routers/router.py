from fastapi import APIRouter

from app.api.routers.downloads import router as downloads_router
from app.api.routers.downloaded_files import (
    router as downloaded_files_router,
)
from app.api.routers.calculations import (
    router as calculations_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(
    downloads_router,
)

api_router.include_router(
    downloaded_files_router,
)

api_router.include_router(
    calculations_router,
)