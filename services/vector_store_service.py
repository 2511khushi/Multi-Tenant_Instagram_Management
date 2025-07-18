from langchain_core.documents import Document
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings
from config.settings import VECTOR_DB_URL, OPENAI_API_KEY

def get_vector_store():
    return PGVector(
        collection_name="vector.embeddings",
        connection_string=VECTOR_DB_URL,
        embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    )

def add_document(store, content, metadata):
    doc = Document(page_content=content)
    store.add_documents([doc], metadata=[metadata])
