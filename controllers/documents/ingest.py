from fastapi import APIRouter, HTTPException
from models.schemas import IngestDocumentsRequest
from database import set_tenant
from utils.loader import load_document_from_url
from services.split_document import split_document
from services.vector_store_service import get_vector_store, add_document  

router = APIRouter()

@router.post("/ingest-documents")
async def ingest_documents(request: IngestDocumentsRequest):
    try:
        set_tenant(request.tenantId)  

        store = get_vector_store()
        success_count = 0

        for url in request.documents:
            try:
                
                content = load_document_from_url(str(url))

                
                chunks = split_document(content)

                
                for chunk in chunks:
                    metadata = {
                        "tenant_id": request.tenantId,
                        "account_id": request.accountId,
                        "object_type": "uploaded_document",
                        "source_url": str(url)
                    }
                    add_document(store, chunk.page_content, metadata)

                success_count += 1

            except Exception as e:
                print(f"Failed to process {url}: {str(e)}")

        return {
            "status": f"Successfully processed {success_count} of {len(request.documents)} documents"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))