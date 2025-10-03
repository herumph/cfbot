import logging
from datetime import datetime, timedelta

from common import DB_SESSION
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from db.models import Base, Game


def get_db_tables(table_name: str) -> Base:
    """Get a database table by name.

    Args:
        table_name (str): name of the table to get

    Returns:
        Base: table class
    """
    tables = Base.__subclasses__()
    for table in tables:
        if table.__tablename__ == table_name:
            return table

    raise ValueError(
        f"Table {table_name} not found in database. Available tables: {[table.__tablename__ for table in tables]}"
    )


def get_a_days_games(start_date: datetime) -> list[Game]:
    """Query the games table for all games on a given date.

    Args:
        start_date: date to query games for

    Returns:
        list[Game]: list of all games
    """
    statement = select(Game).filter(
        (Game.start_ts >= start_date),
        (Game.start_ts <= (start_date + timedelta(days=1))),
    )
    rows = DB_SESSION.execute(statement).all()

    if not len(rows):
        logging.warning(f"No games found for date {start_date.date()}")

    return [row[0] for row in rows]

# TODO: add tests
def get_values(table_name: str, filter: dict) -> list[dict]:
    """Generic interface to get values from a database table.

    Args:
        table_name: table in the database to get values from
        filter: filter to match rows
    Returns:
        list[dict]: list of rows matching the filter
    """
    table = get_db_tables(table_name)
    query = select(table).where(*(getattr(table, k) == v for k, v in filter.items()))
    rows = DB_SESSION.execute(query).all()

    if not len(rows):
        logging.warning(f"No rows found for filter {filter} in table {table_name}")

    return [row[0] for row in rows]



def insert_rows(table_name: str, rows: list[dict]):
    """Generic interface to log rows into a database table.

    Args:
        table_name: table in the database to log to
        rows: rows to insert
    """
    if not len(rows):
        logging.info("No rows to insert")
        return

    DB_SESSION.execute(
        insert(get_db_tables(table_name)).values(rows).on_conflict_do_nothing()
    )
    DB_SESSION.commit()


def add_record(table_name: str, values: dict):
    """Saves a record to the database.

    Args:
        table_name (str): name of the table to log to
        values (dict): dictionary containing the values to log
    """
    if not values:
        logging.info("No values to insert")
        return

    table = get_db_tables(table_name)
    query = table(**values)
    DB_SESSION.add(query)
    DB_SESSION.commit()

# TODO: add tests
def update_rows(table_name: str, values: dict, condition: dict):
    """Generic interface to update rows in a database table.

    Args:
        table_name: table in the database to update
        values: values to update
        condition: condition to match rows to update
    """
    if not values:
        logging.info("No values to update")
        return

    table = get_db_tables(table_name)
    query = (
        update(table)
        .where(*(getattr(table, k) == v for k, v in condition.items()))
        .values(**values)
    )
    DB_SESSION.execute(query)
    DB_SESSION.commit()