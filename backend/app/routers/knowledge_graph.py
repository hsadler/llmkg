import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app import models
from app.database import Database, get_database

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge_graph"])


@router.get(
    "/subject/{subject_name}",
    description="Fetch knowledge graph local by subject and relationship depth.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_knowledge_graph_local_graph(
    subject_name: str,
    relationship_depth: int = Query(default=1, ge=1),
    db: Database = Depends(get_database),
) -> models.KnowledgeGraphOutput:
    logger.info(
        "Fetching subset of knowledge graph by subject", extra={"subject_name": subject_name}
    )
    # related = await subjects_repo.fetch_subject_relations_by_subject_name(db, subject_name)
    # if related is None:
    #     raise HTTPException(status_code=404, detail="Resource not found")
    # kg = models.KnowledgeGraph(
    #     nodes=[
    #         models.KnowledgeGraphNode(
    #             subject_name=subject_name,
    #             related_subject_names=[rs.name for rs in related.related_subjects],
    #         )
    #     ]
    # )
    # return models.KnowledgeGraphOutput(data=kg, meta={})

    # STUB: mock data response
    return models.KnowledgeGraphOutput(
        data=models.KnowledgeGraph(
            nodes=[
                models.KnowledgeGraphNode(subject_name="foo", related_subject_names=["bar"]),
                models.KnowledgeGraphNode(subject_name="bar", related_subject_names=["foo"]),
                models.KnowledgeGraphNode(
                    subject_name=subject_name, related_subject_names=["foo", "bar"]
                ),
                models.KnowledgeGraphNode(
                    subject_name="baz", related_subject_names=["foo", "bar", subject_name]
                ),
            ]
        ),
        meta={},
    )


class APISubjectListOutput(BaseModel):
    data: list[str] = Field(description="General Subjects fetched.")
    meta: dict[str, Any] = Field(description="Metadata about the subjects.")


@router.get(
    "/subjects/general",
    description="Fetch most general subjects.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_general_subjects(db: Database = Depends(get_database)) -> APISubjectListOutput:
    logger.info("Fetching general subjects")
    # STUB: mock data response
    return APISubjectListOutput(
        data=["foo", "bar", "baz"],
        meta={},
    )
