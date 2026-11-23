"""Маршрут главной страницы ресторана."""

from pathlib import Path

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from marusya.seed import RESTAURANT

router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent / "templates",
)


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    """Отображает главную страницу ресторана."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "restaurant": RESTAURANT,
            "demo_mode": request.app.state.demo_mode,
        },
    )
