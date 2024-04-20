import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response

from app import models
from app.database import Database, get_database
from app.repos import subjects as subjects_repo

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
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Resource already exists")
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
