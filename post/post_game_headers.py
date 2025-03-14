"""Create root post about a game that is starting."""

from datetime import datetime, timedelta

from atproto import Client
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.models import Game
from post.create_post import create_post
from query.common import ESPN_TEAM, call_espn


def _update_database(db_session: Session, result: dict[str, str]):
    """Update database with last created post.

    Args:
        db_session (Session): SQLite session
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

    db_session.execute(query)
    db_session.commit()


def _get_team_streak(team_info: dict) -> str:
    """Gather win/loss streaks from ESPN API json.

    Args:
        team_info (dict): ESPN API json response

    Returns:
        string: formatted win/loss streak
    """
    streak = [stat["value"] for stat in team_info["team"]["record"]["items"][0]["stats"] if stat["name"] == "streak"][0]
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
    return away_team + away_team_conference + home_team + home_team_conference + f" has kicked off on {game.networks}!"


def get_current_games(start_date: datetime, db_session: Session) -> list[Game]:
    """Query game table to get currently active games.

    Args:
        start_date (datetime): start date of games to consider

    Returns:
        list[Game]: list of currently ongoing games
    """
    statement = select(Game).filter(
        (Game.start_ts <= start_date),
        (Game.start_ts >= start_date - timedelta(hours=6)),
    )
    rows = db_session.execute(statement).all()

    return [row[0] for row in rows]


def post_about_current_games(date: datetime, db_session: Session, client: Client):
    """Create root level posts for all currently ongoing games.

    Args:
        date (datetime): date to get active games for
    """

    games = get_current_games(date, db_session)
    for game in games:
        if not game.last_post_id:
            streak_info = {}
            for team in [game.home_team_id, game.away_team_id]:
                team_info = call_espn(db_session, ESPN_TEAM + team)
                streak_info[team] = _get_team_streak(team_info)

            post_text = _format_post_text(game, streak_info)
            post = create_post(client, db_session, post_text, "game_header")
            _update_database(db_session, {"game_id": game.id, "last_post_id": post})
