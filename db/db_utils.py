import logging
from datetime import datetime, timedelta

from db import DB_SESSION
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from db.models import Base, Game, Post


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


def get_games(start_date: datetime, end_date: datetime) -> list[Game]:
    """Query the games table for all games on a given date.

    Args:
        start_date: date to query games for

    Returns:
        list[Game]: list of all games
    """
    statement = select(Game).filter(
        (Game.start_ts >= start_date),
        (Game.start_ts <= end_date),
    )
    rows = DB_SESSION.execute(statement).all()

    if not len(rows):
        logging.warning(f"No games found for dates {start_date.date(), end_date.date()}")

    return [row[0] for row in rows]

# TODO: add tests
def has_previous_daily_post(date: datetime) -> bool:
    """Checking if a daily post was made already for a given date.

    Args:
        date (datetime): date to get previous posts for

    Returns:
        bool: if there is a previous daily post
    """
    query = select(Post).filter(
        (Post.created_at_ts >= date - timedelta(hours=24)),
        (Post.created_at_ts <= date),
        (Post.post_type == "daily"),
    )
    rows = DB_SESSION.execute(query).all()
    return len(rows) > 1


# TODO: add tests
def get_values(table_name: str, filter: dict, return_type: str | None = "all") -> list[dict]:
    """Generic interface to get values from a database table. Only operates with equality filters.

    Args:
        table_name: table in the database to get values from
        filter: filter to match rows
    Returns:
        list[dict]: list of rows matching the filter
    """
    table = get_db_tables(table_name)
    query = select(table).where(*(getattr(table, k) == v for k, v in filter.items()))

    if return_type == "all":
        rows = DB_SESSION.execute(query).all()
    elif return_type == "first":
        rows = DB_SESSION.execute(query).first()
    else:
        raise ValueError("return_type must be 'all' or 'first'")

    if not len(rows):
        logging.warning(f"No rows found for filter {filter} in table {table_name}")

    return [row[0] for row in rows] if return_type == "all" else rows[0]



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