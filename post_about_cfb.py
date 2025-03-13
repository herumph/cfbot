"""
Wrapper to call each module needed to get and post about CFB data.
"""
from datetime import datetime, timezone

from post.post_game_headers import post_about_current_games
from post.post_important_plays import post_important_plays
from query.get_games import get_games


def post_about_cfb(date: datetime):
    """Wrapper function to execute each module."""
    get_games(date=date)
    post_about_current_games(date=date)
    post_important_plays(date=date)


if __name__ == "__main__":
    post_about_cfb(datetime.now(timezone.utc))
