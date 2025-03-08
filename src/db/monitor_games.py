"""Wrapper to monitor games and post when scoring occurs.

TODO: delete this file and create a proper handler.
"""

from datetime import datetime, timezone

from post.post_game_headers import get_current_games, post_about_current_games
from post.post_important_plays import post_about_game

if __name__ == "__main__":
    date = datetime.now(timezone.utc)

    # create root game post for each active game
    post_about_current_games(date)

    games = get_current_games(date)
    for game in games:
        post_about_game(game.id)
