"""Conexión a Postgres desde los notebooks.

Uso:
    from src.db import engine, get_connection
    with get_connection() as conn:
        ...
"""
import os
from sqlalchemy import create_engine

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ.get('POSTGRES_HOST', 'db')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ['POSTGRES_DB']}"
)

engine = create_engine(DB_URL, pool_pre_ping=True)


def get_connection():
    """Devuelve una conexión SQLAlchemy para usar con `with`."""
    return engine.connect()
