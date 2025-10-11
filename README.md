# CFBot

This is a bot to monitor CFB games and post updated scores to bluesky.

It uses a SQLite backend to track games that are currently ongoing and track posts that have been made.

## Getting Started
To run this bot run the `post_about_cfb` script

## TO-DO
1. Add unit tests
2. Move bluesky functions to their own package
3.  Fix touchdown/extra point race condition properly
   1.  Add scoring type class?
   2.  Deal with ESPN double "KICK" posting
   3.  Honestly, ignore ESPN `isScore` and parse the result manually with checks - this should also help with turnover posts
       1.  Game with safety: 401405062
       2.  Game with missing PAT: 401628358
       3.  Game with pick six: 
   4.  Why are we not using `scoringPlays` instead? The `id` is the same as the play id and it includes safeties as well.
4.  Have post a days games do something