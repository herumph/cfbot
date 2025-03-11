# CFBot

This is a bot to monitor CFB games and post updated scores to bluesky.

It uses a SQLite backend to track games that are currently ongoing and track posts that have been made.

## Getting Started
To run this bot:

1. Gather games that will occur today by running `python get_games.py`
2. Post scoring updates by running `python monitor_games.py`

## TO-DO
1. Only injest new games -- DONE
2. Add unit tests
3. Organize project
4. Create as a project using `pants` -- DONE
5. Create table for storing credentials -- DONE
6. Move db initialization to the db __init__ file -- Will not do