"""
Create sqlite db and all tables
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base


def init_db_session() -> Session:
    """
    Initialize connection to the sqlite database
    """
    engine = create_engine("sqlite:///database.db")
    Base.metadata.create_all(engine)

    return Session(engine)
