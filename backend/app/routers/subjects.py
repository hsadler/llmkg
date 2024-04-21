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
        subject: models.Subject = await subjects_repo.create_subject(db, input_subject.name)
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
        extra={
            "subject_name": input.subject_name,
            "related_subjects_names": input.related_subject_names,
        },
    )
    # Create all subjects based on subject and related_subjects
    subject: models.Subject = await subjects_repo.fetch_or_create_subject_by_name(
        db, input.subject_name
    )
    related_subjects: list[models.Subject] = []
    for related_subject_name in input.related_subject_names:
        related_subject: models.Subject = await subjects_repo.fetch_or_create_subject_by_name(
            db, related_subject_name
        )
        related_subjects.append(related_subject)
    # Create relationships between subject and related_subjects
    await subjects_repo.create_subject_relations(db, subject, related_subjects)
    return Response(status_code=201)
