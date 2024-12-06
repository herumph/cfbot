"""
Gather games from the ESPN API for a given date and log them to the database
"""

from typing import Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from common import ESPN_SCOREBOARD, call_espn
from create_db import init_db_session
from create_post import create_post
from login import init_client
from models import Game


def get_records(teams: dict[str, str], home_away: str, records: list[dict]) -> dict[str, str]:
    """
    Parse record information from an ESPN API response

    Args:
        teams (dict): dictionary containing information about home and away teams
        home_away (str): string whose value is either 'home' or 'away'
        records (list[dict]): list of record information from the ESPN API

    Returns:
        teams dictionary with total records and conference records populated.
    """
    assert home_away in ("home", "away"), "home_away variable must be either home or away."

    for record in records:
        if record["type"] == "total":
            teams[f"{home_away}_wins"], teams[f"{home_away}_losses"] = record["summary"].split("-")
        elif record["type"] == "vsconf":
            teams[f"{home_away}_conf_wins"], teams[f"{home_away}_conf_losses"] = record["summary"].split("-")

    return teams


def parse_competitors(competitors: list[dict]) -> dict[str, str]:
    """
    Gather competitor information from an ESPN API response

    Args:
        competitiors (list[dict]): list containing all teams involved in a competition

    Returns:
        dictionary containing home and away team names and records
    """
    teams = {}
    for team in competitors:
        teams[f"{team['homeAway']}_team"] = team["team"]["shortDisplayName"]
        teams[f"{team['homeAway']}_team_id"] = team["id"]
        teams = get_records(teams, team["homeAway"], team["records"])

    return teams


def parse_games(game_json: dict) -> list[Game]:
    """
    Parse game information from the ESPN scoreboard

    Args:
        game_json (dict): ESPN API response from the ESPN scoreboard for a given league

    Returns:
        list[Game]: list of Game models to be added to the SQLite database
    """
    games = []
    for event in game_json["events"]:
        competitors = parse_competitors(event["competitions"][0]["competitors"])
        games.append(
            Game(
                id=event["id"],
                start_ts=datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ"),
                networks=event["competitions"][0]["broadcast"],
                home_score=0,
                away_score=0,
                trackable=True,
                **competitors,
            )
        )

    return games


def log_games_to_db(game_data: list[Game]):
    """
    Logs games to SQLite database

    Args:
        game_data (list): list of games to add to the database
    """
    session = init_db_session()
    session.add_all(game_data)

    session.commit()


def get_a_days_games(start_date: datetime) -> list[Game]:
    """
    Query the games table for all games on a given date

    Args:
        start_date: date to query games for

    Returns:
        list[Game]: list of all games
    """
    session = init_db_session()

    statement = select(Game).filter(
        (Game.start_ts >= start_date),
        (Game.start_ts <= (start_date + timedelta(days=1))),
    )
    rows = session.execute(statement).all()

    return [row[0] for row in rows]


def post_a_days_games(todays_games: list[Game]):
    """
    Create a top level post of how many games there are today

    Args:
        todays_games (list[Game]): list of games
    """
    client = init_client()
    session = init_db_session()

    post_text = f"There are {len(todays_games)} college football games today!"
    create_post(client, session, post_text)


def main(date: datetime, selected_teams: Optional[list] = None):
    """
    Gathers games from espn and logs them to the database

    Args:
        date (datetime): date to get games for
        selected_teams Optional[list]: names of teams to add games for
    """
    date = date.strftime("%Y%m%d")
    # group 80 == FBS, 81 == FCS
    game_data = call_espn(ESPN_SCOREBOARD + f"{date}&groups=80")
    games = parse_games(game_data)

    if selected_teams:
        games = [game for game in games if game.home_team in selected_teams or game.away_team in selected_teams]

    log_games_to_db(games)


if __name__ == "__main__":
    date = datetime.now(timezone.utc)
    main(date)
