from fastapi import FastAPI
from controllers import ingestion_controller, reply_controller, caption_controller

app = FastAPI(title="Ingestion Worker API")

app.include_router(ingestion_controller.router, tags=["Ingestion"])
app.include_router(reply_controller.router, tags=["Reply Generation"])
app.include_router(caption_controller.router, tags=["Caption Generation"])

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy"}
