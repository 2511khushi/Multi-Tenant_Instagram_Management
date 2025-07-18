from fastapi import APIRouter, HTTPException
from models.schemas import GenerateCaptionRequest
from services.vision_service import generate_image_description
from services.vector_store_service import get_vector_store
from database import set_tenant
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import OPENAI_API_KEY

router = APIRouter()

@router.post("/generate-caption")
async def generate_caption(request: GenerateCaptionRequest):
    try:
        set_tenant(request.tenantId)
        image_description = generate_image_description(request.imageUrl)
        store = get_vector_store()

        results = store.similarity_search_with_score(
            query=image_description,
            k=10,
            filter={
                "tenant_id": request.tenantId,
                "account_id": request.accountId
            }
        )

        past_captions = []
        business_context = []

        for doc, score in results:
            if score >= 0.4:
                obj_type = doc.metadata.get("object_type")
                if obj_type == "post_caption":
                    past_captions.append(doc)
                elif obj_type == "uploaded_document":
                    business_context.append(doc)

        past_caption_text = "\n\n".join(
            [f"{i+1}. {doc.page_content}" for i, doc in enumerate(past_captions)]
        )
        business_context_text = "\n\n".join(
            [f"- {doc.page_content}" for doc in business_context]
        )

        if not past_caption_text and not business_context_text:
            return {"caption": ""}

        prompt_text = f"""
You are a creative assistant for a business Instagram account.

Business Context (from uploaded documents):
{business_context_text}

Image Description: "{image_description}"

Past post-caption examples:
{past_caption_text}

Write a creative and brand-aligned Instagram caption that matches the business context.
"""

        model = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | model

        response = chain.invoke({"prompt": prompt_text})
        return {"caption": response.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
