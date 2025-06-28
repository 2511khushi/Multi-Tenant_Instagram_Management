from fastapi import APIRouter
from .ingest import router as ingest_router

router = APIRouter()
router.include_router(ingest_router, tags=["Ingestion"])
