import logging

import pydantic
from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.models.pydantic import StorePayloadSchema, StoreSchema
from app.models.tortoise import Store

logger = logging.getLogger("uvicorn")
router = APIRouter()


@router.post("/", response_model=StoreSchema, status_code=201, summary="Register a new store")
async def receive(
    payload: StorePayloadSchema, settings: Settings = Depends(get_settings)
) -> StoreSchema:

    store = await Store.filter(url=payload.url).first()
    if store:
        logger.info(f"Store already exists: {store}")

    else:
        store = Store(url=payload.url)
        await store.save()
        logger.info(f"New store added: {payload.url}")

    return await StoreSchema.from_tortoise_orm(store)


@router.get("/", response_model=StoreSchema, summary="Get a store")
async def get_store(url: pydantic.AnyUrl = Query(...)) -> StoreSchema:
    store = await Store.filter(url=url).first()
    if store:
        return await StoreSchema.from_tortoise_orm(store)

    else:
        raise HTTPException(status_code=404, detail=f"Store: {url} not found")
