import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette import status

from app import models
from app.database import Database, get_database
from app.repos import subjects as subjects_repo

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.post(
    "/",
    description="Find or create a new subject.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
        status.HTTP_200_OK: {"description": "Subject found"},
        status.HTTP_201_CREATED: {"description": "Subject created"},
    },
)
async def find_or_create_subject(
    input_subject: models.SubjectCreate, db: Database = Depends(get_database)
) -> JSONResponse:
    logger.info("Finding or creating new subject", extra={"subject": input_subject})
    try:
        subject = await subjects_repo.fetch_subject_by_name(db, input_subject.name)
        if subject is not None:
            # Existing subject found
            logger.info("Subject found", extra={"subject": dict(subject)})
            return JSONResponse(
                content=jsonable_encoder(models.SubjectOutput(data=subject, meta={})),
                status_code=status.HTTP_200_OK,
            )
        else:
            # Create new subject
            subject = await subjects_repo.create_subject(db, input_subject.name)
            logger.info("Subject created", extra={"subject": dict(subject)})
            return JSONResponse(
                content=jsonable_encoder(models.SubjectOutput(data=subject, meta={})),
                status_code=status.HTTP_201_CREATED,
            )
    except Exception as e:
        logger.exception(
            "Error finding or creating subject",
            extra={"subject_name": input_subject.name, "error": e},
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/{subject_id}",
    description="Get a subject by ID.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
    },
    status_code=status.HTTP_200_OK,
)
async def get_subject_by_id(
    subject_id: int, db: Database = Depends(get_database)
) -> models.SubjectOutput:
    logger.info("Fetching subject by ID", extra={"subject_id": subject_id})
    subjects: list[models.Subject] = await subjects_repo.fetch_subjects_by_ids(db, [subject_id])
    if len(subjects) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return models.SubjectOutput(data=subjects[0], meta={})


@router.post(
    "/related-subjects",
    description="Create related subjects relationships.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
    },
    status_code=status.HTTP_201_CREATED,
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
    return Response(status_code=status.HTTP_201_CREATED)


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
) -> models.RelatedSubjectsOutput:
    logger.info("Fetching related subjects by subject name", extra={"subject_name": subject_name})
    related_subjects = await subjects_repo.fetch_subject_relations_by_subject_name(db, subject_name)
    if related_subjects is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return models.RelatedSubjectsOutput(data=related_subjects, meta={})
