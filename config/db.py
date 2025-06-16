import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")

def get_engine():
    return create_engine(VECTOR_DB_URL)

def set_tenant(tenant_id: str):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(f"SET app.tenant = '{tenant_id}'"))
        conn.commit()
