from dotenv import load_dotenv
import os

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")