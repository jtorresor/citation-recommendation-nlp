from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routes import router

ROOT = Path(__file__).resolve().parents[1]


app = FastAPI(
    title="IntenCite API",
    description="Semantic citation function classification API",
    version="0.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory=ROOT / "app" / "static"),
    name="static",
)


templates = Jinja2Templates(directory=ROOT / "app" / "templates")


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health():

    return {"status": "ok"}


app.include_router(router)
