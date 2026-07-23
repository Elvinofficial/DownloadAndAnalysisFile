from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routers.pages import router as pages_router
from app.api.routers.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(
    pages_router,
)

app.include_router(
    api_router,
)


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }