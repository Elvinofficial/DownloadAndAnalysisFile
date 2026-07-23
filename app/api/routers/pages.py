from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=["Pages"],
)

templates = Jinja2Templates(
    directory="app/templates",
)


@router.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def downloads_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="downloads.html",
    )


@router.get(
    "/downloaded-files",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def downloaded_files_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="downloaded_files.html",
    )