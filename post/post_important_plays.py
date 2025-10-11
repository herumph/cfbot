from datetime import datetime, timedelta

from data.parse_results import get_scoring_plays
from data.query_api import query_game

from post.bluesky_utils import create_post
from db.db_utils import get_games, get_values
from post.format_posts import scoring_play


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

        # format post and send it if the score has gone up
        if (
            result["home_score"] > game_info.home_score
            or result["away_score"] > game_info.away_score
        ):
            post_text = scoring_play(result)
            if (
                "KICK" in post_text
                or "Two-Point" in post_text
                or "FG" in post_text
                or "PAT" in post_text
            ):
                create_post(post_text, "game_update", game_info.last_post_id)


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
