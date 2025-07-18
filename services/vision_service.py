from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config.settings import OPENAI_API_KEY

def generate_image_description(image_url: str) -> str:
    vision_model = ChatOpenAI(
        model="gpt-4o", api_key=OPENAI_API_KEY, max_tokens=200
    )
    
    vision_prompt = [
        HumanMessage(
            content=[
                {"type": "text", "text": "Describe the image in 1–2 short sentences."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )
    ]

    response = vision_model.invoke(vision_prompt)
    return response.content.strip()

