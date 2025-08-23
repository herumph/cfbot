# CFBot

This is a bot to monitor CFB games and post updated scores to bluesky.

It uses a SQLite backend to track games that are currently ongoing and track posts that have been made.

## Getting Started
To run this bot run the `post_about_cfb` script

## TO-DO
1. Only injest new games -- DONE
2. Add unit tests
3. Organize project
4. Create as a project using `pants` -- DONE
5. Create table for storing credentials -- DONE
6. Move db initialization to the db __init__ file -- Will not do
7. Does login type do anything??? -- REMOVED
8. Make db_session and client exist in common and import to each file instead of passing between most functions -- DONE
9. Fix touchdown/extra point race condition properly
   1.  Add scoring type class?
   2.  Deal with ESPN double "KICK" posting
   3.  Honestly, ignore ESPN `isScore` and parse the result manually with checks - this should also help with turnover posts
       1.  Game with safety: 401405062
       2.  Game with missing PAT: 401628358
       3.  Game with pick six: 