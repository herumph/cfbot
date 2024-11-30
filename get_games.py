from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from common import ESPN_SCOREBOARD, call_espn
from create_db import init_db_session
from create_post import create_post
from login import init_client
from models import Game


def get_records(teams: dict, home_away: str, records: list[dict]):
    for record in records:
        if record["type"] == "total":
            teams[f"{home_away}_wins"], teams[f"{home_away}_losses"] = record["summary"].split("-")
        elif record["type"] == "vsconf":
            teams[f"{home_away}_conf_wins"], teams[f"{home_away}_conf_losses"] = record["summary"].split("-")

    return teams


def parse_competitors(competitors: list[dict]):
    teams = {}
    for team in competitors:
        teams[f"{team['homeAway']}_team"] = team["team"]["shortDisplayName"]
        teams[f"{team['homeAway']}_team_id"] = team["id"]
        teams = get_records(teams, team["homeAway"], team["records"])

    return teams


def parse_games(game_json: dict) -> list:
    games = []
    for event in game_json["events"]:
        competitors = parse_competitors(event["competitions"][0]["competitors"])
        games.append(
            Game(
                id=event["id"],
                start_ts=datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ"),
                networks=event["competitions"][0]["broadcast"],
                trackable=True,
                **competitors,
            )
        )

    return games


def log_games_to_db(game_data: list):
    session = init_db_session()
    session.add_all(game_data)

    session.commit()


def get_a_days_games(start_date: datetime) -> list[Game]:
    session = init_db_session()

    statement = select(Game).filter(
        (Game.start_ts >= start_date),
        (Game.start_ts < (start_date + timedelta(days=2))),
    )
    rows = session.execute(statement).all()

    return [row[0] for row in rows]


def post_a_days_games(todays_games: list[Game]):
    client = init_client()
    session = init_db_session()

    post_text = f"There are {len(todays_games)} college football games today!"
    create_post(client, session, post_text)


if __name__ == "__main__":
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    # group 80 == FBS, 81 == FCS
    game_data = call_espn(ESPN_SCOREBOARD + f"{date}&groups=80")
    games = parse_games(game_data)

    log_games_to_db(games)
