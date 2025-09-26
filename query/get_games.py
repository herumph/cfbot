"""Gather games from the ESPN API for a given date and log them to the
database."""
import logging
from datetime import datetime

from db.models import Game
from query.common import ESPN_SCOREBOARD, call_espn
from db.db_utils import insert_values


def get_records(teams: dict[str, str], home_away: str, records: list[dict]) -> dict[str, str]:
    """Parse record information from an ESPN API response.

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
    """Gather competitor information from an ESPN API response.

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


def parse_games(game_json: dict) -> list[dict]:
    """Parse game information from the ESPN scoreboard.

    Args:
        game_json (dict): ESPN API response from the ESPN scoreboard for a given league

    Returns:
        list[dict]: list of games to be added to the SQLite database
    """
    games = []
    for event in game_json["events"]:
        competitors = parse_competitors(event["competitions"][0]["competitors"])
        games.append(
            {
                "id": event["id"],
                "start_ts": datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ"),
                "networks": event["competitions"][0]["broadcast"],
                "home_score": 0,
                "away_score": 0,
                "trackable": True,
                **competitors,
            }
        )

    return games


def log_games_to_db(games: list[dict]):
    """Logs games database.

    Args:
        game_data (list): list of games to add to the database
    """
    if games:
        insert_values(Game, games)
    else:
        logging.info("No games found.")


def get_games(date: datetime, groups: str | None = "80") -> list[dict]:
    """Gathers games from espn and logs them to the database.

    Args:
        date (datetime): date to get games for

    Returns:
        list[dict]: list of each game for a given date
    """
    date = date.strftime("%Y%m%d")
    # group 80 == FBS, 81 == FCS
    game_data = call_espn(ESPN_SCOREBOARD + f"{date}&groups={groups}")
    games = parse_games(game_data)

    log_games_to_db(games=games)
    return games
