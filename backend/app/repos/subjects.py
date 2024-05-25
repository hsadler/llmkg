import logging
from typing import Union
from uuid import UUID

import asyncpg
from pydantic import BaseModel, Field

from app.database import Database

logger = logging.getLogger(__name__)


# Subjects


class SubjectRecord(BaseModel):
    id: int = Field(gt=0, description="Item id. Autoincremented.", example=1)
    uuid: UUID = Field(
        description="Item uuid4 identifier.", example="123e4567-e89b-12d3-a456-426614174000"
    )
    name: str = Field(max_length=50, description="Subject name.", example="cooking")


async def create_subject(db: Database, subject_name: str) -> SubjectRecord:
    INSERT_COMMAND: str = """
        INSERT INTO subject (name)
        VALUES ($1)
        RETURNING id;
    """
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE id = $1
    """
    try:
        async with db.pool.acquire() as con:
            subject_id = await con.fetchval(INSERT_COMMAND, subject_name)
            logger.info("Subject record inserted", extra={"subject_id": subject_id})
            subject_created_record = await con.fetchrow(FETCH_COMMAND, subject_id)
        return SubjectRecord(**subject_created_record)
    except asyncpg.exceptions.UniqueViolationError as e:
        logger.info(
            "Subject record could not be created because it violated a unique constraint",
            extra={"error": e},
        )
        raise e


async def fetch_general_subjects(db: Database, limit: int) -> list[str]:
    FETCH_COMMAND: str = """
        SELECT related_subject_name, COUNT(*) as count
        FROM subject_relation
        GROUP BY related_subject_name
        ORDER BY count DESC
        LIMIT $1
    """
    async with db.pool.acquire() as con:
        fetched_records = await con.fetch(FETCH_COMMAND, limit)
    return [r["related_subject_name"] for r in fetched_records]


async def fetch_subject_by_name(db: Database, subject_name: str) -> Union[SubjectRecord, None]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE name = $1
    """
    async with db.pool.acquire() as con:
        subject_record = await con.fetchrow(FETCH_COMMAND, subject_name)
    return SubjectRecord(**subject_record) if subject_record is not None else None


async def fetch_or_create_subject_by_name(db: Database, subject_name: str) -> SubjectRecord:
    subject = await fetch_subject_by_name(db, subject_name)
    if subject is None:
        subject = await create_subject(db, subject_name)
    return subject


# Subject Relationships


async def create_subject_relations(
    db: Database, subject_name: str, related_subject_names: list[str]
) -> None:
    INSERT_COMMAND: str = """
        INSERT INTO subject_relation (subject_name, related_subject_name)
        VALUES ($1, $2)
    """
    async with db.pool.acquire() as con:
        for related_subject_name in related_subject_names:
            try:
                await con.execute(INSERT_COMMAND, subject_name, related_subject_name)
                logger.info(
                    "Subject relationships created",
                    extra={
                        "subject_name": subject_name,
                        "related_subject_name": related_subject_name,
                    },
                )
            except asyncpg.exceptions.UniqueViolationError as e:
                # Do not re-raise the exception, just log it
                logger.info(
                    "Subject relationship could not be created because it already exists",
                    extra={"error": e},
                )


class SubjectRelationRecord(BaseModel):
    subject_name: str
    related_subject_name: str


async def fetch_subject_relations_by_subject_name(
    db: Database, subject_name: str
) -> list[SubjectRelationRecord]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject_relation
        JOIN subject
        ON subject_relation.related_subject_name = subject.name
        WHERE subject_relation.subject_name = $1
    """
    async with db.pool.acquire() as con:
        fetched_records = await con.fetch(FETCH_COMMAND, subject_name)
        logger.info("Fetched subject relations", extra={"fetched_record": fetched_records})
    logger.info("Fetched subject relations", extra={"fetched_record": fetched_records})
    subject_relation_records: list[SubjectRelationRecord] = []
    for r in fetched_records:
        subject_relation_records.append(SubjectRelationRecord(**r))
    return subject_relation_records
