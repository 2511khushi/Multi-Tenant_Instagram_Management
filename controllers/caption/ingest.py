from fastapi import APIRouter, HTTPException
from models.schemas import IngestPostCaptionAIRequest
from services.vision_service import generate_image_description
from services.vector_store_service import get_vector_store, add_document
from database import set_tenant

router = APIRouter()

@router.post("/ingest-post-caption")
async def ingest_post_caption(request: IngestPostCaptionAIRequest):
    try:
        set_tenant(request.tenantId)
        image_description = generate_image_description(str(request.imageUrl))
        content = f'Post text: "{image_description}" → Caption: "{request.caption}"'

        store = get_vector_store()
        add_document(store, content, {
            "tenant_id": request.tenantId,
            "account_id": request.accountId,
            "object_type": "post_caption",
            "source_id": f"post_{request.postId}"
        })

        return {
            "status": "Post-caption pair ingested",
            "generated_image_description": image_description
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
