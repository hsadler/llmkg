import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app import models
from app.database import Database, get_database

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge_graph"])


class APIKnowledgeGraphOutput(BaseModel):
    data: models.KnowledgeGraph = Field(description="Knowledge Graph portion fetched.")
    meta: dict[str, Any] = Field(description="Metadata about the knowledge graph.")


@router.get(
    "/subject/{subject_name}",
    description="Fetch knowledge local graph by subject and relationship depth.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_knowledge_graph_local_graph(
    subject_name: str,
    relationship_depth: int = Query(default=1, ge=1),
    db: Database = Depends(get_database),
) -> APIKnowledgeGraphOutput:
    logger.info(
        "Fetching subset of knowledge graph by subject", extra={"subject_name": subject_name}
    )

    # STUB: mock data response
    return APIKnowledgeGraphOutput(
        data=models.KnowledgeGraph(
            subjects=[
                models.Subject(
                    name="cooking",
                    related_subjects=["baking", "sushi"],
                )
            ]
        ),
        meta={},
    )
