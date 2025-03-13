"""Wrapper to call each module needed to get and post about CFB data."""
from datetime import datetime, timezone

from db.create_db import init_db_session
from post.login import init_client
from post.post_game_headers import post_about_current_games
from post.post_important_plays import post_important_plays
from query.get_games import get_games


def post_about_cfb(date: datetime, username: str, login_type: str | None = "dev"):
    """Wrapper function to execute each module."""
    db_session = init_db_session()
    client = init_client(db_session=db_session, username=username, login_type=login_type)

    get_games(date=date, db_session=db_session, client=client)
    post_about_current_games(date=date, db_session=db_session, client=client)
    post_important_plays(date=date, db_session=db_session, client=client)


if __name__ == "__main__":
    DATE = datetime.now(timezone.utc)
    USERNAME = "arethegoodnamesaretaken+devbot@gmail.com"
    LOGIN_TYPE = "dev"
    post_about_cfb(date=DATE, username=USERNAME, login_type=LOGIN_TYPE)
