"""Wrapper to call each module needed to get and post about CFB data."""
from datetime import datetime, timezone

from post.post_game_headers import create_game_header_posts, post_a_days_games
from post.post_important_plays import post_important_plays
from query.get_games import get_games

DATE = datetime.now(timezone.utc)


def post_about_cfb(date: datetime):
    """Wrapper function to execute each module."""
    get_games(date=date)
    post_a_days_games(date=date)
    create_game_header_posts(date=date)
    post_important_plays(date=date)


if __name__ == "__main__":
    # DATE = datetime.strptime("2025-01-20 15:00:00", "%Y-%m-%d %H:%M:%S")  # for testing purposes only
    post_about_cfb(date=DATE)
