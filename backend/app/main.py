import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app import models
from app.database import get_database
from app.log import setup_logging
from app.routers.items import router as items_router
from app.routers.subjects import router as subjects_router
from app.routers.knowledge_graph import router as knowledge_graph_router
from app.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    docs_url="/docs",
    title="LLMKG Server",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    if settings.is_prod:
        db = await get_database()
        await db.run_migrations()


@app.on_event("shutdown")
async def shutdown() -> None:
    db = await get_database()
    await db.cleanup()


@app.get("/status", description='Returns `"ok"` if the server is up', tags=["status"])
async def status() -> models.StatusOutput:
    logger.info("Request to /status")
    return models.StatusOutput(status="ok")


app.include_router(items_router)
app.include_router(subjects_router)
app.include_router(knowledge_graph_router)


Instrumentator().instrument(app).expose(app)
