import logging

import pydantic
from fastapi import APIRouter, Depends, Query

from app.config import Settings, get_settings
from app.models.pydantic import Store_Pydantic
from app.models.tortoise import Store

logger = logging.getLogger("uvicorn")
router = APIRouter()


@router.post("/store")
async def receive(url: pydantic.AnyUrl, settings: Settings = Depends(get_settings)):

    store = await Store.filter(url=url).first()
    if store:
        msg = "Store already exists: "
        logger.info(f"{msg}{store}")
        store_obj = await Store_Pydantic.from_tortoise_orm(store)
    else:
        msg = "New store added: "
        store = await Store.create(url=url)
        store_obj = await Store_Pydantic.from_tortoise_orm(store)

        logger.info(f"{msg}{url}")

    return {"message": msg, "url": store_obj.url}


@router.get("/store")
async def get_store(url: pydantic.AnyUrl = Query(...)):
    store = await Store.filter(url=url).first()
    if store:
        store_obj = await Store_Pydantic.from_tortoise_orm(store)
        return store_obj
    else:
        return {"message": "Store not found"}
