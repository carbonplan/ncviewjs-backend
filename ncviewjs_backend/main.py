from fastapi import FastAPI

from .api import datasets, ping
from .logging import get_logger

logger = get_logger()


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router, tags=["ping"])
    application.include_router(datasets.router, tags=["datasets"], prefix="/datasets")
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
