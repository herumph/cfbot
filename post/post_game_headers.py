from datetime import datetime, timedelta

from data.espn_parser import ESPNParser
from data.query_api import query_team

from db.db_utils import get_games, has_previous_daily_post, update_rows
from post.bluesky_utils import create_post
from post.format_posts import game_header


# TODO: This isn't used for anything right now
def post_a_days_games(
    date: datetime, offset: int | None = -5, post_hour: int | None = 7
):
    """Create a top level post of how many games there are today. If a post
    hasn't already been created.

    Args:
        date (datetime): date to post about
        offset (Optional, int): timezone offset from utc, default -5
        post_hour (Optional, int): hour after which to post the daily update, default 7
    """
    todays_games = (
        get_games(date, date + timedelta(hours=24))
        if date.hour + offset >= post_hour
        else None
    )
    if todays_games and has_previous_daily_post(date):
        post_text = f"There are {len(todays_games)} college football games today!"
        create_post(post_text, "daily")


def create_game_header_posts(date: datetime):
    """Create root level posts for all currently ongoing games.

    Args:
        date (datetime): date to get active games for
    """
    games = get_games(date - timedelta(minutes=5), date + timedelta(minutes=5))
    for game in games:
        if not game.last_post_id:
            streak_info = {}
            for team in [game.home_team_id, game.away_team_id]:
                team_info = query_team(team)
                streak_info[team] = ESPNParser.team_streak(team_info)

            post_text = game_header(game, streak_info)
            post_id = create_post(post_text, "game_header")
            update_rows("games", {"last_post_id": post_id}, {"id": game.id})
