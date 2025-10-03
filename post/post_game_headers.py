"""Create root post about a game that is starting."""

from datetime import datetime, timedelta

from data.query_api import query_team
from db.db_utils import get_values, update_rows, has_previous_daily_post, get_games
from post.create_post import create_post
from db.models import Game

# TODO: add tests
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

# TODO: add tests
def format_post_text(game: Game, streak_info: dict[str, str]) -> str:
    """Format information into posting format.

    Args:
        game (Game): game information from the game database
        streak_info (dict[str, str]): dictionary of the streak information for the home and away teams

    Returns:
        string: post text
    """
    away_team = f"{game.away_team} ({game.away_wins}-{game.away_losses}, "
    away_team_conference = f"{(game.away_conf_wins)}-{game.away_conf_losses}) {streak_info[game.away_team_id]} @ "
    home_team = f"{game.home_team} ({game.home_wins}-{game.home_losses}, "
    home_team_conference = f"{game.home_conf_wins}-{game.home_conf_losses}) {streak_info[game.home_team_id]}"
    return (
        away_team
        + away_team_conference
        + home_team
        + home_team_conference
        + f" has kicked off on {game.networks}!"
    )


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
    end_date = date - timedelta(hours=6)
    games = get_games(date, end_date)
    # TODO: This shouldn't be here
    for game in games:
        if not game.last_post_id:
            streak_info = {}
            for team in [game.home_team_id, game.away_team_id]:
                team_info = query_team(team)
                streak_info[team] = get_team_streak(team_info)

            post_text = format_post_text(game, streak_info)
            post_id = create_post(post_text, "game_header")
            update_rows("games", {"last_post_id": post_id}, {"id": game.id})
