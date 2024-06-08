from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class StatusOutput(BaseModel):
    status: str = Field(description="Status of the service.")


# Items EXAMPLES


class ItemIn(BaseModel):
    name: str = Field(max_length=50, description="Item name.", examples=["foo"])
    price: float = Field(gt=0, description="Item price.", examples=[3.14])


class Item(BaseModel):
    id: int = Field(gt=0, description="Item id. Autoincremented.", examples=[1])
    uuid: UUID = Field(
        description="Item uuid4 identifier.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    created_at: datetime = Field(description="Item time created.", examples=["2021-01-01T00:00:00"])
    name: str = Field(max_length=50, description="Item name.", examples=["foo"])
    price: float = Field(gt=0, description="Item price.", examples=[3.14])


class ItemInput(BaseModel):
    data: ItemIn = Field(description="Item to be created.")


class ItemOutput(BaseModel):
    data: Item = Field(description="Item created.")
    meta: dict[str, Any] = Field(description="Metadata about the item.")


class ItemsOutput(BaseModel):
    data: list[Item] = Field(description="Items fetched.")
    meta: dict[str, Any] = Field(description="Metadata about the items.")


# Knowledge Graph


class Subject(BaseModel):
    name: str = Field(description="Subject name.", examples=["cooking"])
    related_subjects: list[str] = Field(
        description="Related subject names.", examples=[["baking", "grilling"]]
    )


class KnowledgeGraph(BaseModel):
    subjects: list[Subject] = Field(description="Subjects within in the knowledge graph.")
