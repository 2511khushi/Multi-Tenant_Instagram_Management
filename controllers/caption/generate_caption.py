from fastapi import APIRouter, HTTPException
from models.schemas import GenerateCaptionRequest
from services.vision_service import generate_image_description
from services.vector_store_service import get_vector_store
from database import set_tenant
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY

router = APIRouter()

@router.post("/generate-caption")
async def generate_caption(request: GenerateCaptionRequest):
    try:
        set_tenant(request.tenantId)
        image_description = generate_image_description(request.imageUrl)
        store = get_vector_store()

        results = store.similarity_search_with_score(
            query=image_description,
            k=5,
            filter={"object_type": "post_caption"}
        )

        filtered = [doc for doc, score in results if score >= 0.7]
        past_content = "\n".join([f"{i+1}.\n{doc.page_content}\n" for i, doc in enumerate(filtered)])

        prompt_text = f"""
You are an assistant helping a business Instagram user.
Image Description: "{image_description}"
Past examples:
{past_content}
Write a creative and relevant caption.
"""

        model = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | model
        response = chain.invoke({"prompt": prompt_text})

        return {"caption": response.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
