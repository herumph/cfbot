"""Create sqlite db and all tables."""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from db.models import Base


def init_db_engine(database_name: str) -> Engine:
    """Initialize database engine"""
    return create_engine(f"sqlite:///{database_name}")


def init_db_session(database_name: str | None = "database.db") -> Session:
    """Initialize connection to the sqlite database."""
    engine = init_db_engine(database_name)
    Base.metadata.create_all(engine)

    return Session(engine)
