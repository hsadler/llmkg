import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app import models
from app.database import get_database
from app.log import setup_logging
from app.routers.items import router as items_router  # example
from app.routers.knowledge_graph import router as knowledge_graph_router
from app.routers.subjects import router as subjects_router
from app.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> Any:
    logger.info("Starting FastAPI lifespan")
    if settings.is_prod:
        db = await get_database()
        await db.run_migrations()
    yield
    logger.info("Ending FastAPI lifespan")
    db = await get_database()
    await db.cleanup()


app = FastAPI(
    docs_url="/docs",
    title="LLMKG Server",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/status", description='Returns `"ok"` if the server is up', tags=["status"])
async def status() -> models.StatusOutput:
    logger.info("Request to /status")
    return models.StatusOutput(status="ok")


app.include_router(items_router)  # example
app.include_router(subjects_router)
app.include_router(knowledge_graph_router)


Instrumentator().instrument(app).expose(app)
