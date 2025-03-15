"""Post scoring plays for a given game."""

from datetime import datetime, timedelta, timezone

from atproto import Client
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.models import Game, Post
from post.create_post import create_post
from post.post_game_headers import get_games
from query.common import ESPN_GAME, call_espn


def _update_database(db_session: Session, result: dict[str, str]):
    """Update database with last post created and if a game is over.

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

    db_session.execute(query)
    db_session.commit()


def _get_previous_posts(db_session: Session, last_post_id: str) -> dict[str, str]:
    """Get information about previous post for a game.

    Args:
        session (Session): SQLite session
        last_post_id (str): id of the last post made

    Returns:
        dict: post information
    """
    query = select(Post).filter(Post.id == last_post_id)
    last_post = db_session.execute(query).first()

    root_id = last_post[0].root_id if last_post[0].root_id else last_post[0].id
    return {
        "parent": last_post[0].id,
        "root": root_id,
        "created_at": last_post[0].created_at,
    }


def get_important_results(game_info: dict) -> list[dict[str, str]]:
    """Gets scoring plays from an ESPN API response and returns them sorted by
    time.

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
        scoring_plays = [play for play in drive["plays"] if play["scoringPlay"]]
        for ind, play in enumerate(scoring_plays):  # yes, there can be multiple scoring plays in one drive according to ESPN
            if drive["isScore"]:
                drive_description = drive["description"] if ind == 0 else None
                results.append(
                    {
                        "game_id": game_info["header"]["id"],
                        "play_text": play["text"],
                        "away_score": play["awayScore"],
                        "home_score": play["homeScore"],
                        "total_score": play["homeScore"] + play["awayScore"],  # needed because ESPN doesn't know how clocks work
                        "drive_description": drive_description,
                        "scoring_team": play["end"]["team"]["id"],
                        "is_complete": is_complete,
                    }
                )

    return sorted(results, key=lambda d: d["total_score"])


def format_scoring_play(drive: dict[str, str]) -> str:
    """Format the scoring play for a drive.

    Args:
        drive (dict): dictionary containing drive information

    Returns:
        string: scoring play formatted for posting
    """
    play_text = f"""{drive["scoring_team"]} scores! {drive["play_text"].strip()}"""
    drive_text = f""" after a drive of {drive["drive_description"]} minutes.\n""" if drive["drive_description"] else ".\n"
    score_text = f"""{drive["away"]} {drive["away_score"]} - {drive["home"]} {drive["home_score"]}"""
    return play_text + drive_text + score_text


def post_important_results(important_results: dict[str, str], db_session: Session, client: Client):
    """Post scoring plays for a game.

    Args:
        important_results (dict): information about the drive's scoring play
    """
    for result in important_results:
        # get information about this game from game table
        query = select(Game).filter(Game.id == result["game_id"])
        game_info = db_session.execute(query).first()[0]
        assert game_info.last_post_id, "No previous post made for this game"
        result["home"] = game_info.home_team
        result["away"] = game_info.away_team
        result["scoring_team"] = game_info.home_team if game_info.home_team_id == result["scoring_team"] else game_info.away_team

        # get parent and root posts from post table
        previous_post = _get_previous_posts(db_session, game_info.last_post_id)

        # format post and send it if the score has gone up
        if result["home_score"] > game_info.home_score or result["away_score"] > game_info.away_score:
            previous_post = {k: v for k, v in previous_post.items() if k in ("parent", "root")}
            post_text = format_scoring_play(result)
            result["last_post_id"] = create_post(client, db_session, post_text, previous_post, "game_update")

            # update database with new information
            _update_database(db_session, result)


def post_about_game(game_id: str, db_session: Session, client: Client):
    """Create bluesky posts about scoring plays for a game.

    Args:
        game_id (str): id of the game in the game table
        date (datetime): datetime of the earliest drive to consider posting about
    """
    game_info = call_espn(db_session, ESPN_GAME + game_id)
    important_results = get_important_results(game_info)

    post_important_results(important_results, db_session, client)


def post_important_plays(date: datetime, db_session: Session, client: Client):
    """Reply to game header posts with important plays, e.g. scoring plays.

    Args:
        date (datetime): date to query against
        db_session (Session): database session
        client (Client): login client
    """
    games = get_games(date, date + timedelta(hours=1), db_session)
    for game in games:
        post_about_game(game["id"], db_session, client)
