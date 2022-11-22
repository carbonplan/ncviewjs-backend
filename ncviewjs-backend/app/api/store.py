import logging

import pydantic
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.models.pydantic import Store_Pydantic
from app.models.tortoise import Store

logger = logging.getLogger("uvicorn")
router = APIRouter()


@router.post("/store")
async def receive(url: pydantic.AnyUrl, settings: Settings = Depends(get_settings)):

    store = await Store.filter(url=url).first()
    if store:
        logger.info(f"Store already exists: {store}")
        store_obj = await Store_Pydantic.from_tortoise_orm(store)
    else:
        store = await Store.create(url=url)
        store_obj = await Store_Pydantic.from_tortoise_orm(store)
        logger.info(f"New store added: {url}")

    return JSONResponse(content={'url': store_obj.url}, status_code=201)


@router.get("/store")
async def get_store(url: pydantic.AnyUrl = Query(...)):
    store = await Store.filter(url=url).first()
    if store:
        return await Store_Pydantic.from_tortoise_orm(store)

    else:
        raise HTTPException(status_code=404, detail=f"Store: {url} not found")
