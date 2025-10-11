from datetime import datetime, timedelta

from data.query_api import query_team
from db.db_utils import update_rows, has_previous_daily_post, get_games
from post.bluesky_utils import create_post
from post.format_posts import game_header

# TODO: add tests, move to espn_parser
def get_team_streak(team_info: dict) -> str:
    """Gather win/loss streaks from ESPN API json.

    Args:
        team_info (dict): ESPN API json response

    Returns:
        string: formatted win/loss streak
    """
    streak = [
        stat["value"]
        for stat in team_info["team"]["record"]["items"][0]["stats"]
        if stat["name"] == "streak"
    ][0]
    streak = f"W{streak}" if streak >= 0 else f"L{str(streak).strip('-')}"
    return str(streak)[:-2]


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
                streak_info[team] = get_team_streak(team_info)

            post_text = game_header(game, streak_info)
            post_id = create_post(post_text, "game_header")
            update_rows("games", {"last_post_id": post_id}, {"id": game.id})
