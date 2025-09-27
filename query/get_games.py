from datetime import datetime

from db.db_utils import insert_rows
from query.query_api import query_scoreboard
from query.parse_results import parse_games


def get_games(date: datetime, group: str | None = "80") -> None:
    """Gathers games from espn and logs them to the database.

    Args:
        date (datetime): date to get games for
        group (str | None): ESPN group to query. 80 == FBS, 81 == FCS. Default value is 80.
    """
    date = date.strftime("%Y%m%d")
    game_data = query_scoreboard(date, group)
    games = parse_games(game_data)

    insert_rows("games", games)
