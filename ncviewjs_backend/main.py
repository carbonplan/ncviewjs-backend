from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import datasets, health, runs
from .logging import get_logger

logger = get_logger()


@asynccontextmanager
async def lifespan_event(app: FastAPI):
    logger.info("Application startup...")
    yield
    logger.info("Application shutdown...")


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan_event)
    # TODO: figure out how to set origins to only the frontend domain
    # in the meantime, we can allow everything.
    # in the future we can set origins to any port on localhost and vercel domains
    origins = ["*"]  # is this dangerous? I don't think so, but I'm not sure.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router, tags=["health"], prefix='/health')
    application.include_router(datasets.router, tags=["datasets"], prefix="/datasets")
    application.include_router(runs.router, tags=["runs"], prefix="/runs")
    return application


app = create_application()
