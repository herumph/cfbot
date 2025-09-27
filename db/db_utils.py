import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from common import DB_SESSION
from db.models import Base, Game, Query


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


def insert_rows(table: Base, rows: list[dict]):
    """Generic interface to log rows into a database table.

    Args:
        table: table in the database to log to
        rows: rows to insert
    """
    if not len(rows):
        logging.info("No rows to insert")
        return

    DB_SESSION.execute(insert(table).values(rows).on_conflict_do_nothing())
    DB_SESSION.commit()


def save_api_query(url: str, status_code: int):
    """Saves a query to the database.

    Args:
        url (str): url that was queried
        status_code (int): status code of the api response
    """
    query = Query(url=url, status_code=status_code, date_ts=datetime.now(timezone.utc))
    DB_SESSION.add(query)
    DB_SESSION.commit()
