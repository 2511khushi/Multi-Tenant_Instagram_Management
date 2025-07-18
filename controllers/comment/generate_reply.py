from fastapi import APIRouter, HTTPException
from models.schemas import GenerateReplyRequest
from services.vector_store_service import get_vector_store
from database import set_tenant
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import OPENAI_API_KEY

router = APIRouter()

@router.post("/generate-reply")
async def generate_reply(request: GenerateReplyRequest):
    try:
        set_tenant(request.tenantId)
        store = get_vector_store()

        results = store.similarity_search_with_score(
            request.commentText,
            k=10,
            filter={
                "tenant_id": request.tenantId,
                "account_id": request.accountId
            }
        )

        relevant_comment_replies = []
        relevant_docs = []

        for doc, score in results:
            if score >= 0.75:
                if doc.metadata.get("object_type") == "comment_reply":
                    relevant_comment_replies.append(doc)
                elif doc.metadata.get("object_type") == "uploaded_document":
                    relevant_docs.append(doc)

        past_threads = "\n\n".join([
            f"{i+1}. {doc.page_content}" for i, doc in enumerate(relevant_comment_replies)
        ])

        business_context = "\n\n".join([
            f"- {doc.page_content}" for doc in relevant_docs
        ])

        if not past_threads and not business_context:
            return {"reply": ""}

        prompt_text = f"""
You are an assistant for a business Instagram account.

Business Context (from uploaded documents):
{business_context}

Comment: "{request.commentText}"

Relevant past comment-reply examples:
{past_threads}

Based on the above context and examples, write a precise, helpful, and business-relevant reply to this comment.
"""

        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | model

        response = chain.invoke({"prompt": prompt_text})
        return {"reply": response.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
