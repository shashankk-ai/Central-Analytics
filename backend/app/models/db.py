"""SQLite persistence for data the app owns outright (currently just the
editable Payment Terms Master) — as opposed to data that lives in Zoho
Analytics, which is always fetched live, never duplicated here.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'central_analytics.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import excluded_vendors, payment_terms  # noqa: F401 — register models with Base

    Base.metadata.create_all(bind=engine)
