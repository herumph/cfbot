from datetime import datetime, timedelta

from db.models import Base, Game
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from common import DB_SESSION


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

    return [row[0] for row in rows]


def insert_values(table: Base, rows: list[dict]):
    """Generic interface to log rows into a database table.

    Args:
        table: table in the database to log to
        rows: rows to insert
    """
    DB_SESSION.execute(insert(table).values(rows).on_conflict_do_nothing())
    DB_SESSION.commit()
