from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="IntenCite API",
    description="Semantic citation function classification API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "IntenCite API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


app.include_router(router)
