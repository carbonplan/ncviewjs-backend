from fastapi import Depends, FastAPI

from .config import Settings, get_settings

app = FastAPI()


@app.get('/ping')
async def ping(settings: Settings = Depends(get_settings)):
    return {'ping': 'pong!', 'environment': settings.environment, 'testing': settings.testing}
