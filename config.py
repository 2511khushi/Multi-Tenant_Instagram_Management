import os
from dotenv import load_dotenv

load_dotenv()
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
