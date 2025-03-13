# what does this actually need to do?
# 1 - get a days games --> how often does this update and how do we update the data in the database? new table?
# 2 - post a days games if needed --> how is this post specific tracked in the database? ^use a new table for this with a post id column
# 3 - post game headers
# 4 - post important plays
from datetime import datetime, timezone

from query.get_games import get_games
from post.post_game_headers import post_about_current_games
from post.post_important_plays import post_important_plays

def post_about_cfb(date: datetime):
    """Wrapper function to execute each module"""
    get_games(date=date)
    post_about_current_games(date=date)
    post_important_plays(date=date)
    

if __name__ == "__main__":
    post_about_cfb(datetime.now(timezone.utc))
