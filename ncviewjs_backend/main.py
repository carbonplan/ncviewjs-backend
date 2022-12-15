import subprocess

from fastapi import FastAPI

from .api import datasets, ping, runs
from .config import get_settings
from .logging import get_logger

logger = get_logger()


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router, tags=["ping"])
    application.include_router(datasets.router, tags=["datasets"], prefix="/datasets")
    application.include_router(runs.router, tags=["runs"], prefix="/runs")
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    if settings.environment == 'prod':
        logger.info("Initializing skyplane...")
        subprocess.check_call(
            "skyplane init -y --disable-config-azure --disable-config-gcp", shell=True
        )
        logger.info("Successfully initialized skyplane")
    logger.info("Application startup...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
