import logging
from typing import Union

import asyncpg

from app import models
from app.database import Database

logger = logging.getLogger(__name__)


# Subjects


async def create_subject(db: Database, subject_name: str) -> models.Subject:
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
        return models.Subject(**subject_created_record)
    except asyncpg.exceptions.UniqueViolationError as e:
        logger.info(
            "Subject record could not be created because it violated a unique constraint",
            extra={"error": e},
        )
        raise e


async def fetch_subject_by_name(db: Database, subject_name: str) -> Union[models.Subject, None]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE name = $1
    """
    async with db.pool.acquire() as con:
        subject_record = await con.fetchrow(FETCH_COMMAND, subject_name)
    return models.Subject(**subject_record) if subject_record is not None else None


async def fetch_or_create_subject_by_name(db: Database, subject_name: str) -> models.Subject:
    subject = await fetch_subject_by_name(db, subject_name)
    if subject is None:
        subject = await create_subject(db, subject_name)
    return subject


async def fetch_subjects_by_ids(db: Database, subject_ids: list[int]) -> list[models.Subject]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE id = ANY($1::int[])
    """
    async with db.pool.acquire() as con:
        fetched_records = await con.fetch(FETCH_COMMAND, subject_ids)
    return [models.Subject(**r) for r in fetched_records]


# Subject Relationships


async def create_subject_relations(
    db: Database, subject: models.Subject, related_subjects: list[models.Subject]
) -> None:
    INSERT_COMMAND: str = """
        INSERT INTO subject_relation (subject_name, related_subject_name)
        VALUES ($1, $2)
    """
    async with db.pool.acquire() as con:
        for related_subject in related_subjects:
            try:
                await con.execute(INSERT_COMMAND, subject.name, related_subject.name)
                logger.info(
                    "Subject relationships created",
                    extra={
                        "subject_name": subject.name,
                        "related_subject_name": related_subject.name,
                    },
                )
            except asyncpg.exceptions.UniqueViolationError as e:
                logger.info(
                    "Subject relationship could not be created because it already exists",
                    extra={"error": e},
                )
