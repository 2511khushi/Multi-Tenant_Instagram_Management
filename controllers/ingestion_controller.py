from fastapi import APIRouter, HTTPException
from models.request_models import IngestCommentsRepliesRequest
from config.db import set_tenant
from services.facebook_service import fetch_comments, fetch_replies
from services.vector_service import get_vector_store
from services.utils import format_comment_thread, split_document

router = APIRouter()

@router.post("/ingest-comments-replies")
async def ingest_comments_replies(request: IngestCommentsRepliesRequest):
    try:
        set_tenant(request.tenantId)
        store = get_vector_store()

        comments = fetch_comments(request.postId, request.accessToken)
        if not comments:
            raise HTTPException(status_code=400, detail="No comments fetched")

        success_count = 0
        for comment in comments:
            comment_text = comment.get("text", "").strip()
            if not comment_text:
                continue

            replies = fetch_replies(comment.get("id", ""), request.accessToken)
            formatted_thread = format_comment_thread(comment_text, replies)
            docs = split_document(formatted_thread)

            store.add_documents(
                docs,
                metadata=[{
                    "tenant_id": request.tenantId,
                    "account_id": request.accountId,
                    "object_type": "comment_thread",
                    "comment_id": comment.get("id", "")
                }] * len(docs)
            )
            success_count += 1

        return {"status": f"Processed {success_count} of {len(comments)} comment threads"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
