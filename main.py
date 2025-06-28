from fastapi import FastAPI
from controllers.comment import router as comment_router
from controllers.caption import router as caption_router
from controllers.documents import router as document_router

app = FastAPI(title="Social Media Assistant API")

app.include_router(comment_router)
app.include_router(caption_router)
app.include_router(document_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
