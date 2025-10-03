"""Post scoring plays for a given game."""

from datetime import datetime, timedelta, timezone

from common import DB_SESSION
from data.parse_results import get_scoring_plays
from data.query_api import query_game
from sqlalchemy import select, update

from db.models import Game, Post
from post.create_post import create_post
from post.post_game_headers import get_games


def _update_database(result: dict[str, str]):
    """Update database with last post created and if a game is over.

    Args:
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

    DB_SESSION.execute(query)
    DB_SESSION.commit()


def _get_previous_posts(last_post_id: str) -> dict[str, str]:
    """Get information about previous post for a game.

    Args:
        last_post_id (str): id of the last post made

    Returns:
        dict: post information
    """
    query = select(Post).filter(Post.id == last_post_id)
    last_post = DB_SESSION.execute(query).first()

    root_id = last_post[0].root_id if last_post[0].root_id else last_post[0].id
    return {
        "parent": last_post[0].id,
        "root": root_id,
        "created_at": last_post[0].created_at,
    }


def format_scoring_play(drive: dict[str, str]) -> str:
    """Format the scoring play for a drive.

    Args:
        drive (dict): dictionary containing drive information

    Returns:
        string: scoring play formatted for posting
    """
    play_text = f"""{drive["scoring_team"]} scores! {drive["play_text"].strip()}"""
    drive_text = (
        f""" after a drive of {drive["drive_description"]} minutes.\n"""
        if drive["drive_description"]
        else ".\n"
    )
    score_text = f"""{drive["away"]} {drive["away_score"]} - {drive["home"]} {drive["home_score"]}"""
    return play_text + drive_text + score_text


def post_important_results(important_results: dict[str, str]):
    """Post scoring plays for a game.

    Args:
        important_results (dict): information about the drive's scoring play
    """
    for result in important_results:
        # get information about this game from game table
        query = select(Game).filter(Game.id == result["game_id"])
        game_info = DB_SESSION.execute(query).first()[0]
        assert game_info.last_post_id, "No previous post made for this game"
        result["home"] = game_info.home_team
        result["away"] = game_info.away_team
        result["scoring_team"] = (
            game_info.home_team
            if game_info.home_team_id == result["scoring_team"]
            else game_info.away_team
        )

        # get parent and root posts from post table
        previous_post = _get_previous_posts(game_info.last_post_id)

        # format post and send it if the score has gone up
        if (
            result["home_score"] > game_info.home_score
            or result["away_score"] > game_info.away_score
        ):
            previous_post = {
                k: v for k, v in previous_post.items() if k in ("parent", "root")
            }
            post_text = format_scoring_play(result)
            if (
                "KICK" in post_text
                or "Two-Point" in post_text
                or "FG" in post_text
                or "PAT" in post_text
            ):
                result["last_post_id"] = create_post(
                    post_text, previous_post, "game_update"
                )

                # update database with new information
                _update_database(result)


def post_about_game(game_id: str):
    """Create bluesky posts about scoring plays for a game.

    Args:
        game_id (str): id of the game in the game table
        date (datetime): datetime of the earliest drive to consider posting about
    """
    game_info = query_game(game_id)
    scoring_plays = get_scoring_plays(game_info)

    post_important_results(scoring_plays)


def post_important_plays(date: datetime):
    """Reply to game header posts with important plays, e.g. scoring plays.

    Args:
        date (datetime): date to query against
    """
    games = get_games(date, date + timedelta(hours=1))
    for game in games:
        post_about_game(game.id)
