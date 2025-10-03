"""Create root post about a game that is starting."""

from datetime import datetime, timedelta

from common import DB_SESSION
from data.query_api import query_team
from sqlalchemy import select, update

from db.models import Game, Post
from post.create_post import create_post


def _update_database(result: dict[str, str]):
    """Update database with last created post.

    Args:
        DB_SESSION (Session): SQLite session
        result (dict[str, str]): dictionary containing game_id and last_post_id
    """
    query = (
        update(Game)
        .where(Game.id == result["game_id"])
        .values(
            {
                "last_post_id": result["last_post_id"],
            }
        )
    )

    DB_SESSION.execute(query)
    DB_SESSION.commit()


def _get_team_streak(team_info: dict) -> str:
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


def _format_post_text(game: Game, streak_info: dict[str, str]) -> str:
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


def get_games(start_date: datetime, end_date: datetime) -> list[Game]:
    """Query game table to get currently active games.

    Args:
        start_date (datetime): start date of games to consider

    Returns:
        list[Game]: list of currently ongoing games
    """
    query = select(Game).filter(
        (Game.start_ts <= end_date),
        (Game.start_ts >= start_date),
    )
    rows = DB_SESSION.execute(query).all()

    return [row[0] for row in rows]


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


def has_previous_daily_post(date: datetime) -> bool:
    """Checking if a daily post was made already for a given date.

    Args:
        date (datetime): date to get previous posts for

    Returns:
        bool: if there is a previous daily post
    """
    query = select(Post).filter(
        (Post.created_at_ts >= date - timedelta(hours=24)),
        (Post.created_at_ts <= date),
        (Post.post_type == "daily"),
    )
    rows = DB_SESSION.execute(query).all()
    return len(rows) > 1


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
                streak_info[team] = _get_team_streak(team_info)

            post_text = _format_post_text(game, streak_info)
            post = create_post(post_text, "game_header")
            _update_database({"game_id": game.id, "last_post_id": post})
