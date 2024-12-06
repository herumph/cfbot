"""
Post scoring plays for a given game
"""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from common import ESPN_GAME, call_espn
from create_db import init_db_session
from create_post import create_post
from login import init_client
from models import Game, Post


def _update_database(session: Session, result: dict[str, str]):
    """
    Update database with last post created and if a game is over

    Args:
        session (Session): SQLite session
        result (dict): dictionary containing last_post_id, game_id, and is_complete
    """
    end_ts = datetime.now(timezone.utc) if result["is_complete"] else None
    query = (
        update(Game)
        .where(Game.id == result["game_id"])
        .values(
            {
                "last_post_id": result["last_post_id"],
                "home_score": result["home_score"],
                "away_score": result["away_score"],
                "end_ts": end_ts,
            }
        )
    )
    session.execute(query)
    session.commit()


def _get_previous_posts(session: Session, last_post_id: str) -> dict[str, str]:
    """
    Get information about previous post for a game

    Args:
        session (Session): SQLite session
        last_post_id (str): id of the last post made

    Returns:
        dict: post information
    """
    query = select(Post).filter(Post.id == last_post_id)
    last_post = session.execute(query).first()

    root_id = last_post[0].root_id if last_post[0].root_id else last_post[0].id
    return {
        "parent": last_post[0].id,
        "root": root_id,
        "created_at": last_post[0].created_at,
    }


def get_important_results(game_info: dict) -> list[dict[str, str]]:
    """
    Get scoring plays from an ESPN API response

    Args:
        game_info (dict): ESPN API response

    Returns:
        list[dict]: list containing all scoring plays from the game that haven't been posted about yet
    """
    results = []
    if "drives" not in game_info.keys():
        return results
    if "previous" not in game_info["drives"].keys():
        return results

    is_complete = game_info["header"]["competitions"][0]["status"]["type"]["completed"]
    all_drives = game_info["drives"]["previous"]
    for drive in all_drives:
        last_play = drive["plays"][-1]
        last_play_time = datetime.strptime(last_play["wallclock"], "%Y-%m-%dT%H:%M:%SZ")
        if drive["isScore"]:
            results.append(
                {
                    "game_id": game_info["header"]["id"],
                    "update_time": last_play_time,
                    "play_text": last_play["text"],
                    "away_score": last_play["awayScore"],
                    "home_score": last_play["homeScore"],
                    "drive_description": drive["description"],
                    "scoring_team": last_play["end"]["team"]["id"],
                    "is_complete": is_complete,
                }
            )

    return results


def format_scoring_play(drive: dict[str, str]) -> str:
    """
    Format the scoring play for a drive

    Args:
        drive (dict): dictionary containing drive information

    Returns:
        string: scoring play formatted for posting
    """
    return f"""{drive["scoring_team"]} scores! {drive["play_text"].strip()} after a drive of {drive["drive_description"]} minutes.\n{drive["away"]} {drive["away_score"]} - {drive["home"]} {drive["home_score"]}"""


def post_important_results(important_results: dict[str, str]):
    """
    Post scoring plays for a game

    Args:
        important_results (dict): information about the drive's scoring play
    """
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
        previous_post = _get_previous_posts(session, game_info.last_post_id)

        # format post and send it if the score has gone up
        if result["home_score"] > game_info.home_score or result["away_score"] > game_info.away_score:
            previous_post = {k: v for k, v in previous_post.items() if k in ("parent", "root")}
            post_text = format_scoring_play(result)
            print(previous_post)
            result["last_post_id"] = create_post(client, session, post_text, previous_post)

            # update database with new information
            _update_database(session, result)


def post_about_game(game_id: str):
    """
    Create bluesky posts about scoring plays for a game

    Args:
        game_id (str): id of the game in the game table
        date (datetime): datetime of the earliest drive to consider posting about
    """
    game_info = call_espn(ESPN_GAME + game_id)
    important_results = get_important_results(game_info)

    post_important_results(important_results)
