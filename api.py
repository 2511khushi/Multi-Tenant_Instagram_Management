import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

app = FastAPI(title="Ingestion Worker API")

INSTAGRAM_API_URL = "https://graph.facebook.com/v23.0"
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# --------- Models ---------
class IngestCommentsRepliesRequest(BaseModel):
    tenantId: str
    accountId: str
    postId: str
    accessToken: str

class GenerateReplyRequest(BaseModel):
    tenantId: str
    accountId: str
    postId: str
    commentText: str

class GenerateCaptionRequest(BaseModel):
    tenantId: str
    accountId: str
    imageDescription: str 


# --------- Helper Functions ---------
def set_tenant(tenant_id: str):
    """Set tenant for Row-Level-Security in PostgreSQL."""
    engine = create_engine(VECTOR_DB_URL)
    with engine.connect() as conn:
        conn.execute(text(f"SET app.tenant = '{tenant_id}'"))
        conn.commit()

def fetch_comments(post_id: str, access_token: str):
    """Fetch comments from a Facebook/Instagram post."""
    url = f"https://graph.facebook.com/{post_id}/comments?access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        comments = response.json().get("data", [])
        return comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def fetch_replies(comment_id: str, access_token: str):
    """Fetch replies to a comment."""
    url = f"https://graph.facebook.com/{comment_id}/replies?access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        replies = response.json().get("data", [])
        return replies
    except Exception as e:
        print(f"Error fetching replies for comment {comment_id}: {e}")
        return []

def format_comment_thread(comment_text: str, replies: list):
    """Format the comment + replies as one document."""
    formatted = f"Comment: \"{comment_text}\"\nReplies:\n"
    for reply in replies:
        reply_text = reply.get("text", "").strip()
        if reply_text:
            formatted += f"- {reply_text}\n"
    return formatted


# --------- API Endpoints ---------

@app.post("/ingest-comments-replies", tags=["Ingestion"])
async def ingest_comments_replies(request: IngestCommentsRepliesRequest):
    """Ingest comment threads into vector DB."""
    try:
        set_tenant(request.tenantId)

        # Init vector store
        store = PGVector(
            collection_name="vector.embeddings",
            connection_string=VECTOR_DB_URL,
            embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        )

        # Fetch comments
        comments = fetch_comments(request.postId, request.accessToken)
        if not comments:
            raise HTTPException(status_code=400, detail="No comments fetched")

        success_count = 0

        for comment in comments:

            print(f"Comment: {comment}")
            comment_text = comment.get("text", "").strip()

            print(f"Comment Text: {comment_text}")
            comment_id = comment.get("id", "")

            # Skip empty comments
            if not comment_text:    
                print(f"Comment Skipped")
                continue

            # Fetch replies for this comment
            replies = fetch_replies(comment_id, request.accessToken)

            print(f"Replies: {replies}")

            # Format the thread
            formatted_thread = format_comment_thread(comment_text, replies)

            # Split into chunks (if needed)
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=160)
            docs = splitter.create_documents([formatted_thread])

            # Store in vector DB
            store.add_documents(
                docs,
                metadata=[
                    {
                        "tenant_id": request.tenantId,
                        "account_id": request.accountId,
                        "object_type": "comment_thread",
                        "comment_id": comment_id
                    }
                ] * len(docs)
            )

            success_count += 1

        return {"status": f"Processed {success_count} of {len(comments)} comment threads"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-reply", tags=["Reply Generation"])
async def generate_reply(request: GenerateReplyRequest):
    """Generate a reply to a new comment using RAG with similarity threshold."""
    try:
        set_tenant(request.tenantId)

        SIMILARITY_THRESHOLD = 0.75 

        # Init vector store
        store = PGVector(
            collection_name="vector.embeddings",
            connection_string=VECTOR_DB_URL,
            embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        )

        # Query top 3 relevant threads with scores
        results_with_score = store.similarity_search_with_score(request.commentText, k=3)

        # Filter results above similarity threshold
        filtered_results = [doc for doc, score in results_with_score if score >= SIMILARITY_THRESHOLD]

        if len(filtered_results) == 0:
            return {"reply": ""}

        # Build the past conversations block
        past_threads = ""
        for i, doc in enumerate(filtered_results, start=1):
            past_threads += f"{i}.\n{doc.page_content}\n\n"

        # Build prompt
        prompt_text = f"""
You are an Instagram business account assistant.
Your job is to generate helpful and friendly replies to user comments. 
If you do not find anything meaningful from past conversations, pass empty string as a reply.

Here is a new comment you need to reply to:

Comment: "{request.commentText}"

Here are some relevant past conversations:

{past_threads}

Generate a helpful and friendly reply to the new comment. Be polite and relevant.

Please be precise because this is a comment reply. 
"""

        # Call GPT-3.5
        chat_model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | chat_model

        reply = chain.invoke({"prompt": prompt_text})

        return {"reply": reply.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-caption", tags=["Caption Generation"])
async def generate_caption(request: GenerateCaptionRequest):
    """Generate a personalized Instagram caption for a new post using RAG."""
    try:
        set_tenant(request.tenantId)

        SIMILARITY_THRESHOLD = 0.7  # Can be tuned

        # Init vector store
        store = PGVector(
            collection_name="vector.embeddings",
            connection_string=VECTOR_DB_URL,
            embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        )

        # Query relevant user data based on the new image's description
        results_with_score = store.similarity_search_with_score(
            query=request.imageDescription,
            k=5
        )

        filtered_results = [doc for doc, score in results_with_score if score >= SIMILARITY_THRESHOLD]

        if not filtered_results:
            return {"caption": ""}

        past_content = ""
        for i, doc in enumerate(filtered_results, start=1):
            past_content += f"{i}.\n{doc.page_content}\n\n"

        # Build the prompt
        prompt_text = f"""
You are an assistant helping a business Instagram user create engaging and relevant captions.

Here are some examples of past posts and comment threads from this user:
{past_content}

Now, the user is planning to post a new image. Here's a description of the image:

"{request.imageDescription}"

Generate a personalized, creative, and audience-relevant caption for this new Instagram post. Keep the caption short, expressive, and aligned with the user's past tone and themes.
"""

        chat_model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | chat_model

        result = chain.invoke({"prompt": prompt_text})

        return {"caption": result.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Check the health of the API."""
    return {"status": "healthy"}

# --------- Run App ---------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
