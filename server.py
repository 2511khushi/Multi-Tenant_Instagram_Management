from typing import Dict, Any, List
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rag")

BASE_URL = "http://localhost:8000"  

# 1. Ingest Post Caption Tool
@mcp.tool()
async def ingest_post_caption(accountId: str, tenantId: str, postId: str, caption: str, imageUrl: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/ingest-post-caption", json={
                "accountId": accountId,
                "tenantId": tenantId,
                "postId": postId,
                "caption": caption,
                "imageUrl": imageUrl
            }, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Ingest post-caption failed: {str(e)}"}

# 2. Ingest Comment-Reply Tool
@mcp.tool()
async def ingest_comment_replies(accountId: str, tenantId: str, postId: str, accessToken: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/ingest-comments-replies", json={
                "accountId": accountId,
                "tenantId": tenantId,
                "postId": postId,
                "accessToken": accessToken
            }, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Ingest comment-reply failed: {str(e)}"}

# 3. Ingest Document Tool
@mcp.tool()
async def ingest_documents(accountId: str, tenantId: str, documents: List[str]) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/ingest-documents", json={
                "accountId": accountId,
                "tenantId": tenantId,
                "documents": documents
            }, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Ingest documents failed: {str(e)}"}

# 4. Generate Caption Tool
@mcp.tool()
async def generate_caption(accountId: str, tenantId: str, imageUrl: str) -> Dict[str, Any]:
    """
    Generate a brand-aligned Instagram caption using image and business context.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/generate-caption", json={
                "accountId": accountId,
                "tenantId": tenantId,
                "imageUrl": imageUrl
            }, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Generate caption failed: {str(e)}"}

# 5. Generate Reply Tool
@mcp.tool()
async def generate_reply(accountId: str, tenantId: str, commentText: str) -> Dict[str, Any]:
    """
    Generate a context-aware reply to a user comment using RAG + business docs.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/generate-reply", json={
                "accountId": accountId,
                "tenantId": tenantId,
                "commentText": commentText
            }, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Generate reply failed: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
