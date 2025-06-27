from sqlalchemy import create_engine, text
from config import VECTOR_DB_URL

def set_tenant(tenant_id: str):
    engine = create_engine(VECTOR_DB_URL)
    with engine.connect() as conn:
        conn.execute(text(f"SET app.tenant = '{tenant_id}'"))
        conn.commit()
