from fastapi import APIRouter, Depends

from ..config import Settings, get_settings

router = APIRouter()


@router.get('/')
def status():
    return {'status': 'ok'}


@router.get("/ping")
async def ping(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "ping": "pong",
        "environment": settings.environment,
        "testing": settings.testing,
    }
