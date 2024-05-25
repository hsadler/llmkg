import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from starlette import status

from app.database import Database, get_database
from app.models import Subject
from app.repos import subjects as subjects_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/subjects", tags=["subjects"])


class APISubjectOutput(BaseModel):
    data: Subject = Field(description="Subject found or created.")
    meta: dict[str, Any] = Field(description="Metadata about the subject.")


@router.post(
    "/",
    description="Find or create a Subject.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
    },
)
async def find_or_create_subject_by_name(
    subject_name: str = Query(min_length=1, example="cooking"), db: Database = Depends(get_database)
) -> APISubjectOutput:
    logger.info("Finding or creating new subject", extra={"subject_name": subject_name})
    try:
        subject_record = await subjects_repo.fetch_subject_by_name(db, subject_name=subject_name)
        if subject_record is not None:
            # Existing subject found
            logger.info("Subject found", extra={"subject_record": dict(subject_record)})
        else:
            # Create new subject
            subject_record = await subjects_repo.create_subject(db, subject_name=subject_name)
            logger.info("Subject created", extra={"subject_record": dict(subject_record)})
        logger.info(
            "Fetching related subjects by subject name", extra={"subject_name": subject_name}
        )
        subject_relation_records = await subjects_repo.fetch_subject_relations_by_subject_name(
            db, subject_name
        )
        subject = Subject(
            name=subject_record.name,
            related_subjects=[r.related_subject_name for r in subject_relation_records],
        )
        return APISubjectOutput(data=subject, meta={})
    except Exception as e:
        logger.exception(
            "Error finding or creating subject",
            extra={"subject_name": subject_name, "error": e},
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIRelatedSubjectsCreate(BaseModel):
    subject_name: str = Field(description="Subject name.", example="cooking")
    related_subject_names: list[str] = Field(
        description="Related subject names.", example=["baking", "sushi"]
    )


@router.post(
    "/related-subjects",
    description="Create related subjects relationships.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_related_subjects(
    input: APIRelatedSubjectsCreate, db: Database = Depends(get_database)
) -> Response:
    logger.info(
        "Creating related subjects relationships",
        extra={
            "subject_name": input.subject_name,
            "related_subjects_names": input.related_subject_names,
        },
    )
    try:
        # Create all subjects based on subject and related_subjects
        await subjects_repo.fetch_or_create_subject_by_name(db, input.subject_name)
        for related_subject_name in input.related_subject_names:
            await subjects_repo.fetch_or_create_subject_by_name(db, related_subject_name)
        # Create relationships between subject and related_subjects
        await subjects_repo.create_subject_relations(
            db, input.subject_name, input.related_subject_names
        )
    except Exception as e:
        logger.exception(
            "Error creating related subjects relationships",
            extra={
                "subject_name": input.subject_name,
                "related_subjects_names": input.related_subject_names,
                "error": e,
            },
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_201_CREATED)


class APISubjectListOutput(BaseModel):
    data: list[str] = Field(description="General Subjects fetched.")
    meta: dict[str, Any] = Field(description="Metadata about the subjects.")


@router.get(
    "/general",
    description="Fetch most general subjects.",
    responses={
        "404": {"description": "Resource not found"},
    },
)
async def get_general_subjects(
    limit: int = Query(default=10, ge=1, le=100), db: Database = Depends(get_database)
) -> APISubjectListOutput:
    logger.info("Fetching general subjects with limit", extra={"limit": limit})
    try:
        general_subjects = await subjects_repo.fetch_general_subjects(db, limit)
        return APISubjectListOutput(data=general_subjects, meta={})
    except Exception as e:
        logger.exception("Error fetching general subjects", extra={"error": e})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
