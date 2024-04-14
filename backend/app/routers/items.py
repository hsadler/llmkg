import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app import models
from app.database import Database, get_database
from app.repos import items as items_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/items", tags=["items"])


@router.get(
    "/{item_id}",
    description="Fetch single item by id.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_item(
    item_id: int = Path(gt=0, example=1), db: Database = Depends(get_database)
) -> models.ItemOutput:
    logger.info("Fetching item by id", extra={"item_id": item_id})
    try:
        item = await items_repo.fetch_item_by_id(db, item_id)
    except Exception as e:
        logger.exception("Error fetching item by id", extra={"item_id": item_id, "error": e})
        raise HTTPException(status_code=500)
    if item is None:
        raise HTTPException(status_code=404, detail="Item resource not found")
    logger.info("Item fetched", extra={"item": dict(item)})
    return models.ItemOutput(data=item, meta={})


@router.get("", description="Fetch multiple items by ids.")
async def get_items(
    item_ids: list[int] = Query(gt=0, example=[1, 2]), db: Database = Depends(get_database)
) -> models.ItemsOutput:
    logger.info("Fetching items by ids", extra={"item_ids": item_ids})
    try:
        items = await items_repo.fetch_items_by_ids(db, item_ids)
    except Exception as e:
        logger.exception("Error fetching items by ids", extra={"item_ids": item_ids, "error": e})
        raise HTTPException(status_code=500)
    logger.info("Items fetched", extra={"items": [dict(item) for item in items]})
    return models.ItemsOutput(data=items, meta={})


@router.post(
    "",
    description="Save new item.",
    responses={
        "409": {"description": "Resource already exists"},
    },
    status_code=201,
)
async def create_item(
    input: models.ItemInput, db: Database = Depends(get_database)
) -> models.ItemOutput:
    item_in = input.data
    logger.info("Inserting item", extra={"item": dict(item_in)})

    try:
        item_created = await items_repo.create_item(db, item_in)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Resource already exists")
    except Exception as e:
        logger.exception("Error while creating item", extra={"error": e})
        raise HTTPException(status_code=500)

    logger.info("Created item", extra={"item": dict(item_created)})
    return models.ItemOutput(data=item_created, meta={"created": True})
