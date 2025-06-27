from fastapi import APIRouter, HTTPException
from models.schemas import GenerateReplyRequest
from services.vector_store_service import get_vector_store
from database import set_tenant
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY

router = APIRouter()

@router.post("/generate-reply")
async def generate_reply(request: GenerateReplyRequest):
    try:
        set_tenant(request.tenantId)
        store = get_vector_store()

        results = store.similarity_search_with_score(request.commentText, k=3)
        relevant = [doc for doc, score in results if score >= 0.75]

        if not relevant:
            return {"reply": ""}

        past_threads = "\n\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(relevant)])
        prompt_text = f"""
You are an Instagram business account assistant.
Comment: "{request.commentText}"
Relevant past comment-reply examples:
{past_threads}
Now write a precise, helpful reply to this comment.
"""

        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | model

        response = chain.invoke({"prompt": prompt_text})
        return {"reply": response.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
