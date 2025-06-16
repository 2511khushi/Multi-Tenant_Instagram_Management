import os
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_vector_store():
    return PGVector(
        collection_name="vector.embeddings",
        connection_string=VECTOR_DB_URL,
        embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    )
