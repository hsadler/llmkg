import logging

# import asyncpg
from fastapi import APIRouter, Depends, Path

from app import models
from app.database import Database, get_database

# from app.repos import items as items_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge_graph"])


@router.get(
    "/subject/{subject}",
    description="Fetch subset of knowledge graph by subject.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_item(
    subject: str = Path(min_length=1), db: Database = Depends(get_database)
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
