from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from common import ESPN_TEAM, call_espn
from create_db import init_db_session
from create_post import create_post
from login import init_client
from models import Game


def _update_database(session: Session, result: dict):
    query = (
        update(Game)
        .where(Game.id == result["game_id"])
        .values(
            {
                "last_post_id": result["last_post_id"],
            }
        )
    )

    session.execute(query)
    session.commit()


def _get_team_streak(team_info: dict) -> str:
    streak = [stat["value"] for stat in team_info["team"]["record"]["items"][0]["stats"] if stat["name"] == "streak"][0]
    streak = f"W{streak}" if streak >= 0 else f"L{str(streak).strip('-')}"
    return str(streak)[:-2]


def _format_post_text(game: Game, streak_info: dict) -> str:
    # return "Clemson (8-2, 4-2) W3 @ Virginia Tech (4-3, 1-3) L1 has kicked off on ESPN!"
    away_team = f"{game.away_team} ({game.away_wins}-{game.away_losses}, {(game.away_conf_wins)}-{game.away_conf_losses}) {streak_info[game.away_team_id]} @ "
    home_away = f"{game.home_team}({game.home_wins}-{game.home_losses}, {game.home_conf_wins}-{game.home_conf_losses}) {streak_info[game.home_team_id]}"
    return away_team + home_away + f" has kicked off on {game.networks}!"


def get_current_games(start_date: datetime) -> list[Game]:
    session = init_db_session()
    statement = select(Game).filter(
        (Game.start_ts <= start_date),
        (Game.start_ts >= start_date - timedelta(hours=6)),
        (Game.last_post_id == None),
    )
    rows = session.execute(statement).all()

    return [row[0] for row in rows]


def post_about_current_games(date: datetime):
    client = init_client()
    session = init_db_session()

    games = get_current_games(date)
    for game in games:
        streak_info = {}
        for team in [game.home_team_id, game.away_team_id]:
            team_info = call_espn(ESPN_TEAM + team)
            streak_info[team] = _get_team_streak(team_info)

        post_text = _format_post_text(game, streak_info)
        post = create_post(client, session, post_text)
        _update_database(session, {"game_id": game.id, "last_post_id": post})


if __name__ == "__main__":
    date = datetime.utcnow()

    post_about_current_games(date)
