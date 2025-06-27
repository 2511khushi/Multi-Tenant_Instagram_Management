from fastapi import APIRouter
from .generate_caption import router as generate_caption_router
from .ingest import router as ingest_caption_router

router = APIRouter()
router.include_router(generate_caption_router, tags=["Caption Generation"])
router.include_router(ingest_caption_router, tags=["Ingestion"])
