from fastapi import APIRouter
from .ingest import router as ingest_router
from .generate_reply import router as generate_reply_router

router = APIRouter()
router.include_router(ingest_router, tags=["Ingestion"])
router.include_router(generate_reply_router, tags=["Reply Generation"])
