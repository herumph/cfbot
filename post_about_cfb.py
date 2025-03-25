"""Wrapper to call each module needed to get and post about CFB data."""
from datetime import datetime, timezone

from db.create_db import init_db_session
from post.login import init_client
from post.post_game_headers import create_game_header_posts, post_a_days_games
from post.post_important_plays import post_important_plays
from query.get_games import get_games

DATE = datetime.now(timezone.utc)
USERNAME = "arethegoodnamesaretaken+devbot@gmail.com"


def post_about_cfb(date: datetime, username: str):
    """Wrapper function to execute each module."""
    db_session = init_db_session()
    client = init_client(db_session=db_session, username=username)

    get_games(date=date, db_session=db_session)
    post_a_days_games(date=date, db_session=db_session, client=client)
    create_game_header_posts(date=date, db_session=db_session, client=client)
    post_important_plays(date=date, db_session=db_session, client=client)


if __name__ == "__main__":
    # DATE = datetime.strptime("2025-01-20 15:00:00", "%Y-%m-%d %H:%M:%S")  # for testing purposes only
    post_about_cfb(date=DATE, username=USERNAME)
