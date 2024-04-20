import logging
import uuid

# import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response

from app import models
from app.database import Database, get_database
from app.repos import subjects as subjects_repo

# from app.repos import items as items_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.post(
    "/",
    description="Create a new subject.",
    responses={
        "400": {"description": "Invalid input"},
    },
    status_code=201,
)
async def create_subject(
    input_subject: models.SubjectCreate, db: Database = Depends(get_database)
) -> models.SubjectOutput:
    logger.info("Creating new subject", extra={"subject": input_subject})
    try:
        subject: models.Subject = await subjects_repo.create_subject(db, input_subject)
        logger.info("Subject created", extra={"subject": dict(subject)})
        return models.SubjectOutput(data=subject, meta={})
    except Exception as e:
        logger.exception(
            "Error creating subject", extra={"subject_name": input_subject.name, "error": e}
        )
        raise HTTPException(status_code=500)


@router.post(
    "/related-subjects",
    description="Create related subjects relationships.",
    responses={
        "400": {"description": "Invalid input"},
    },
    status_code=201,
)
async def create_related_subjects(
    input: models.RelatedSubjectsCreate, db: Database = Depends(get_database)
) -> Response:
    logger.info(
        "Creating related subjects relationships",
        extra={"subject": input.subject, "related_subjects": input.related_subjects},
    )
    # STUB: mock data response
    return Response(status_code=201)


@router.get(
    "/general",
    description="Fetch general subjects.",
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
