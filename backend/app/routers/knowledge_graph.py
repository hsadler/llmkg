import logging
import uuid

# import asyncpg
from fastapi import APIRouter, Depends, Path

from app import models
from app.database import Database, get_database

# from app.repos import items as items_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge_graph"])


@router.get(
    "/subject/{subject}",
    description="Fetch knowledge graph local by subject and relationship depth.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_knowledge_graph_local_graph(
    subject: str = Path(min_length=1),
    relationship_depth: int = Path(ge=0),
    db: Database = Depends(get_database),
) -> models.KnowledgeGraphOutput:
    logger.info("Fetching subset of knowledge graph by subject", extra={"subject": subject})
    # STUB: mock data response
    return models.KnowledgeGraphOutput(
        data=models.KnowledgeGraph(
            nodes=[
                models.KnowledgeGraphNode(subject="foo", related_subjects=["bar"]),
                models.KnowledgeGraphNode(subject="bar", related_subjects=["foo"]),
                models.KnowledgeGraphNode(subject=subject, related_subjects=["foo", "bar"]),
                models.KnowledgeGraphNode(subject="baz", related_subjects=["foo", "bar", subject]),
            ]
        ),
        meta={},
    )


@router.get(
    "/subjects/general",
    description="Fetch most general subjects.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_general_subjects(db: Database = Depends(get_database)) -> models.SubjectListOutput:
    logger.info("Fetching general subjects")
    # STUB: mock data response
    return models.SubjectListOutput(
        data=[
            models.Subject(
                id=1, uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"), name="cooking"
            ),
            models.Subject(
                id=2, uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174001"), name="baking"
            ),
        ],
        meta={},
    )
