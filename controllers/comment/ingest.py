from fastapi import APIRouter, HTTPException
from models.schemas import IngestCommentsRepliesRequest
from services import facebook_service, vector_store_service
from services.vector_store_service import get_vector_store
from database import set_tenant
from utils.formatter import format_comment_reply_pair

router = APIRouter()

@router.post("/ingest-comments-replies")
async def ingest_comments_replies(request: IngestCommentsRepliesRequest):
    try:
        set_tenant(request.tenantId)
        store = get_vector_store()

        comments = facebook_service.fetch_comments(request.postId, request.accessToken)
        if not comments:
            raise HTTPException(status_code=400, detail="No comments found")

        count = 0
        for comment in comments:
            comment_text = comment.get("text", "").strip()
            if not comment_text:
                continue
            comment_id = comment.get("id", "")
            replies = facebook_service.fetch_replies(comment_id, request.accessToken)

            for reply in replies:
                reply_text = reply.get("text", "").strip()
                if not reply_text:
                    continue
                content = format_comment_reply_pair(comment_text, reply_text)
                vector_store_service.add_document(store, content, {
                    "tenant_id": request.tenantId,
                    "account_id": request.accountId,
                    "object_type": "comment_reply",
                    "source_id": f"comment_{comment_id}"
                })
                count += 1

        return {"status": f"Processed {count} comment-reply pairs"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
