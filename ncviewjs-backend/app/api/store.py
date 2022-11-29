import logging

import pydantic
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.helpers import sanitize_url
from app.models.pydantic import StorePayloadSchema, StoreSchema
from app.models.tortoise import Store
from app.store_validation import validate_zarr_store

logger = logging.getLogger("uvicorn")
router = APIRouter()


async def _validate_store(*, store: StoreSchema) -> None:
    """Validate that the store is accessible"""
    try:
        validate_zarr_store(store.url)
    except Exception as exc:
        data = dict(status="completed", conclusion="failure", error_message=str(exc))

        await Store.filter(id=store.id).update(**data)
        logger.error(f'Validation of store: {store.url} failed: {exc}')


@router.post("/", response_model=StoreSchema, status_code=201, summary="Register a new store")
async def receive(
    payload: StorePayloadSchema,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
) -> StoreSchema:

    # Sanitize the URL
    sanitized_url = sanitize_url(payload.url)

    db_store = await Store.filter(
        md5_id=sanitized_url.md5_id, protocol=sanitized_url.protocol
    ).first()
    if db_store:
        logger.info(f"Store already exists: {db_store}")
        store = await StoreSchema.from_tortoise_orm(db_store)

    else:
        db_store = Store(
            url=sanitized_url.url,
            md5_id=sanitized_url.md5_id,
            protocol=sanitized_url.protocol,
            bucket=sanitized_url.bucket,
            key=sanitized_url.key,
        )
        await db_store.save()
        logger.info(f"New store added: {payload.url}")
        store = await StoreSchema.from_tortoise_orm(db_store)
        background_tasks.add_task(_validate_store, store=store)
    return store


@router.get("/", response_model=StoreSchema, summary="Get a store")
async def get_store(url: pydantic.AnyUrl = Query(...)) -> StoreSchema:

    # Sanitize the URL
    sanitized_url = sanitize_url(url)

    store = await Store.filter(md5_id=sanitized_url.md5_id, protocol=sanitized_url.protocol).first()
    if store:
        return await StoreSchema.from_tortoise_orm(store)

    else:
        raise HTTPException(status_code=404, detail=f"Store: {url} not found")
