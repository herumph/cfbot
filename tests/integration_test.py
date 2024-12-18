"""
Testing E2E -- importing in order
"""
import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from datetime import datetime, timedelta

from get_games import main
from post_game_headers import get_current_games, post_about_current_games
from post_important_plays import post_about_game

# testing with this BYU game because there is some weird data in there
# https://www.espn.com/college-football/game/_/gameId/401636942/houston-byu

START_DATE = "2024-11-30"
START_DATE = datetime.strptime(START_DATE, "%Y-%m-%d")

# get games
main(START_DATE, ["BYU"])

# make header post
START_DATE = START_DATE + timedelta(hours=31)
post_about_current_games(START_DATE)

# post scoring plays
games = get_current_games(START_DATE)
for game in games:
    post_about_game(game.id)
