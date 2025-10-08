from datetime import datetime, timedelta, timezone

from data.parse_results import get_scoring_plays
from data.query_api import query_game

from post.bluesky_utils import create_post
from db.db_utils import get_games, update_rows, get_values


# TODO: add tests
def update_database(result: dict[str, str]):
    """Update database with last post created and if a game is over.

    Args:
        result (dict): dictionary containing last_post_id, game_id, and is_complete
    """
    end_ts = datetime.now(timezone.utc) if result["is_complete"] else None
    update_rows(
        "games",
        {
            "last_post_id": result["last_post_id"],
            "home_score": result["home_score"],
            "away_score": result["away_score"],
            "end_ts": end_ts,
        },
        {"id": result["game_id"]},
    )


# TODO: add tests
def get_previous_posts(last_post_id: str) -> dict[str, str]:
    """Get information about previous post for a game.

    Args:
        last_post_id (str): id of the last post made

    Returns:
        dict: post information
    """
    last_post = get_values("posts", {"id": last_post_id}, "first")

    return {
        "parent": last_post.id,
        "root": last_post.root_id if last_post.root_id else last_post.id,
        "created_at": last_post.created_at_ts,
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


def post_scoring_plays(important_results: list[dict]):
    """Post scoring plays for a game.

    Args:
        important_results (dict): information about the drive's scoring play
    """
    for result in important_results:
        game_info = get_values("games", {"id": result["game_id"]}, "first")
        if game_info.last_post_id is None:
            continue

        result["home"] = game_info.home_team
        result["away"] = game_info.away_team
        result["scoring_team"] = (
            game_info.home_team
            if game_info.home_team_id == result["scoring_team"]
            else game_info.away_team
        )

        # get parent and root posts from post table
        previous_post = get_previous_posts(game_info.last_post_id)

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
                    post_text,
                    "game_update",
                    previous_post,
                )

                # update database with new information
                update_database(result)


def post_about_game(game_id: str):
    """Create bluesky posts about scoring plays for a game.

    Args:
        game_id (str): id of the game in the game table
        date (datetime): datetime of the earliest drive to consider posting about
    """
    game_info = query_game(game_id)
    scoring_plays = get_scoring_plays(game_info)

    post_scoring_plays(scoring_plays)


def post_important_plays(date: datetime):
    """Reply to game header posts with important plays, e.g. scoring plays.

    Args:
        date (datetime): date to query against
    """
    games = get_games(date - timedelta(days=1), date)
    for game in games:
        post_about_game(game.id)
