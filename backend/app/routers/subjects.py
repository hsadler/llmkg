import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from starlette import status

from app.database import Database, get_database
from app.repos import subjects as subjects_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/subjects", tags=["subjects"])


class APISubjectOutput(BaseModel):
    data: subjects_repo.SubjectRecord = Field(description="Subject found or created.")
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
        subject = await subjects_repo.fetch_subject_by_name(db, subject_name=subject_name)
        if subject is not None:
            # Existing subject found
            logger.info("Subject found", extra={"subject": dict(subject)})
        else:
            # Create new subject
            subject = await subjects_repo.create_subject(db, subject_name=subject_name)
            logger.info("Subject created", extra={"subject": dict(subject)})
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


class APIRelatedSubjectsOutput(BaseModel):
    data: list[str] = Field(description="Related Subjects found.")
    meta: dict[str, Any] = Field(description="Metadata about the related subjects.")


@router.get(
    "/related-subjects/{subject_name}",
    description="Get related subjects by subject name.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
    },
    status_code=status.HTTP_200_OK,
)
async def get_related_subjects_by_subject_name(
    subject_name: str, db: Database = Depends(get_database)
) -> APIRelatedSubjectsOutput:
    logger.info("Fetching related subjects by subject name", extra={"subject_name": subject_name})
    try:
        subject_relation_records = await subjects_repo.fetch_subject_relations_by_subject_name(
            db, subject_name
        )
    except Exception as e:
        logger.exception(
            "Error fetching related subjects by subject name",
            extra={"subject_name": subject_name, "error": e},
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return APIRelatedSubjectsOutput(
        data=[r.related_subject_name for r in subject_relation_records], meta={}
    )
