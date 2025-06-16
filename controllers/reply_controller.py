from fastapi import APIRouter, HTTPException
from models.request_models import GenerateReplyRequest
from config.db import set_tenant
from services.vector_service import get_vector_store
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

router = APIRouter()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/generate-reply")
async def generate_reply(request: GenerateReplyRequest):
    try:
        set_tenant(request.tenantId)

        SIMILARITY_THRESHOLD = 0.75
        store = get_vector_store()
        results_with_score = store.similarity_search_with_score(request.commentText, k=3)
        filtered = [doc for doc, score in results_with_score if score >= SIMILARITY_THRESHOLD]

        if not filtered:
            return {"reply": ""}

        past_threads = "\n\n".join([f"{i+1}.\n{doc.page_content}" for i, doc in enumerate(filtered)])

        prompt_text = f"""
You are an Instagram business account assistant.
Your job is to generate helpful and friendly replies to user comments.

Comment: "{request.commentText}"

Relevant past conversations:
{past_threads}

Generate a polite, relevant reply.
"""

        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        reply = (prompt | model).invoke({"prompt": prompt_text})

        return {"reply": reply.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
