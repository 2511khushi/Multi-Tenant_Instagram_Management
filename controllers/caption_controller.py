from fastapi import APIRouter, HTTPException
from models.request_models import GenerateCaptionRequest
from config.db import set_tenant
from services.vector_service import get_vector_store
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

router = APIRouter()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/generate-caption")
async def generate_caption(request: GenerateCaptionRequest):
    try:
        set_tenant(request.tenantId)

        SIMILARITY_THRESHOLD = 0.7
        store = get_vector_store()
        results_with_score = store.similarity_search_with_score(request.imageDescription, k=5)
        filtered = [doc for doc, score in results_with_score if score >= SIMILARITY_THRESHOLD]

        if not filtered:
            return {"caption": ""}

        past_content = "\n\n".join([f"{i+1}.\n{doc.page_content}" for i, doc in enumerate(filtered)])

        prompt_text = f"""
You are helping a business Instagram user generate a caption.

Image Description: "{request.imageDescription}"

Based on past content:
{past_content}

Generate a short, expressive, relevant caption.
"""

        model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        caption = (prompt | model).invoke({"prompt": prompt_text})

        return {"caption": caption.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
