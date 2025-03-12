import pytest
from sqlalchemy import inspect

from db.create_db import init_db_engine
from db.models import Base


@pytest.fixture(scope="session")
def db_engine():
    return init_db_engine("database.db")


# test for database table names
def test_table_names(db_engine):
    """Test for table names."""
    Base.metadata.create_all(db_engine)

    expected_tables = {"games", "credentials", "posts"}
    actual_tables = inspect(db_engine).get_table_names()

    assert expected_tables == set(actual_tables)
