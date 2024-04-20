import logging
from typing import Union

import asyncpg

from app import models
from app.database import Database

logger = logging.getLogger(__name__)


async def fetch_subject_by_name(db: Database, subject_name: str) -> Union[models.Subject, None]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE name = $1
    """
    async with db.pool.acquire() as con:
        subject_record = await con.fetchrow(FETCH_COMMAND, subject_name)
    return models.Subject(**subject_record) if subject_record is not None else None


async def fetch_subjects_by_ids(db: Database, subject_ids: list[int]) -> list[models.Subject]:
    FETCH_COMMAND: str = """
        SELECT * FROM subject
        WHERE id = ANY($1::int[])
    """
    async with db.pool.acquire() as con:
        fetched_records = await con.fetch(FETCH_COMMAND, subject_ids)
    return [models.Subject(**r) for r in fetched_records]


async def create_subject(db: Database, input_subject: models.SubjectCreate) -> models.Subject:
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
            subject_id = await con.fetchval(INSERT_COMMAND, input_subject.name)
            logger.info("Subject record inserted", extra={"subject_id": subject_id})
            subject_created_record = await con.fetchrow(FETCH_COMMAND, subject_id)
        return models.Subject(**subject_created_record)
    except asyncpg.exceptions.UniqueViolationError as e:
        logger.info(
            "Subject record could not be created because it violated a unique constraint",
            extra={"error": e},
        )
        raise e
