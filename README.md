# CFBot

This is a bot to monitor CFB games and post updated scores to bluesky.

It uses a SQLite backend to track games that are currently ongoing and track posts that have been made.

## Getting Started
The python environment is described in `conda_env.yml`.

To run this bot:

1. Gather games that will occur today by running `python get_games.py`
2. Post scoring updates by running `python monitor_games.py`