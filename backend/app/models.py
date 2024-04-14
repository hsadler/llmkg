from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class StatusOutput(BaseModel):
    status: str = Field(description="Status of the service.")


class ItemIn(BaseModel):
    name: str = Field(max_length=50, description="Item name.", example="foo")
    price: float = Field(gt=0, description="Item price.", example="3.14")


class Item(BaseModel):
    id: int = Field(gt=0, description="Item id. Autoincremented.", example=1)
    uuid: UUID = Field(
        description="Item uuid4 identifier.", example="123e4567-e89b-12d3-a456-426614174000"
    )
    created_at: datetime = Field(
        description="Item time created.", example="2021-01-01T00:00:00.000000"
    )
    name: str = Field(max_length=50, description="Item name.", example="foo")
    price: float = Field(gt=0, description="Item price.", example="3.14")


class ItemInput(BaseModel):
    data: ItemIn = Field(description="Item to be created.")


class ItemOutput(BaseModel):
    data: Item = Field(description="Item created.")
    meta: dict[str, Any] = Field(description="Metadata about the item.")


class ItemsOutput(BaseModel):
    data: list[Item] = Field(description="Items fetched.")
    meta: dict[str, Any] = Field(description="Metadata about the items.")
