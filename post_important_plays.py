from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from common import ESPN_GAME, call_espn
from create_db import init_db_session
from create_post import create_post
from login import init_client
from models import Game, Post


def _update_database(session: Session, result: dict):
    end_ts = datetime.utcnow() if result["is_complete"] else None
    query = (
        update(Game)
        .where(Game.id == result["game_id"])
        .values(
            {
                "last_post_id": result["last_post_id"],
                "end_ts": end_ts,
            }
        )
    )
    session.execute(query)
    session.commit()


def _get_previous_posts(session: Session, game_info: dict) -> dict:
    # queries for post information
    query = select(Post).filter(Post.id == game_info.last_post_id)
    last_post = session.execute(query).first()

    return {
        "parent": last_post[0].id,
        "root": last_post[0].root_id,
        "created_at": last_post[0].created_at,
    }


def get_important_results(game_info: dict, last_updated: datetime) -> list:
    results = []
    if "drives" not in game_info.keys():
        return results
    if "previous" not in game_info["drives"].keys():
        return results

    is_complete = game_info["header"]["competitions"][0]["status"]["type"]["completed"]
    previous_drives = game_info["drives"]["previous"]
    for drive in previous_drives:
        last_play = drive["plays"][-1]
        last_play_time = datetime.strptime(last_play["wallclock"], "%Y-%m-%dT%H:%M:%SZ")
        if drive["isScore"] and last_play_time > last_updated:
            scoring_team_id = last_play["end"]["team"]["id"]
            results.append(
                {
                    "game_id": game_info["header"]["id"],
                    "update_time": last_play_time,
                    "play_text": last_play["text"],
                    "away_score": last_play["awayScore"],
                    "home_score": last_play["homeScore"],
                    "drive_description": drive["description"],
                    "scoring_team": scoring_team_id,
                    "is_complete": is_complete,
                }
            )

    return results


def format_scoring_play(drive: dict) -> str:
    return f"""{drive["scoring_team"]} scores! {drive["play_text"].strip()} after a drive of {drive["drive_description"]} minutes.\n{drive["away"]} {drive["away_score"]} - {drive["home"]} {drive["home_score"]}"""


def post_important_results(important_results: dict):
    client = init_client()
    session = init_db_session()

    for result in important_results:
        # get information about this game from game table
        query = select(Game).filter(Game.id == result["game_id"])
        game_info = session.execute(query).first()[0]
        assert game_info.last_post_id, "No previous post made for this game"
        result["home"] = game_info.home_team
        result["away"] = game_info.away_team
        result["scoring_team"] = game_info.home_team if game_info.home_team_id == result["scoring_team"] else game_info.away_team

        # get parent and root posts from post table
        previous_post = _get_previous_posts(session, game_info)

        # format post and send it
        if result["update_time"] > previous_post["created_at"]:
            previous_post = {k: v for k, v in previous_post.items() if k == "parent" or k == "root"}
            post_text = format_scoring_play(result)
            result["last_post_id"] = create_post(client, session, post_text, previous_post)

            # update database with new information
            _update_database(session, result)


def post_about_game(game_id: str, date: datetime):
    game_info = call_espn(ESPN_GAME + game_id)
    important_results = get_important_results(game_info, date)

    post_important_results(important_results)


if __name__ == "__main__":
    game_id = "401645366"
    post_about_game(game_id, datetime.utcnow() - timedelta(minutes=5))
