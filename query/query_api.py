from query.espn_api import ESPNAPI


def query_scoreboard(date: str, group: str) -> dict:
    """Query the ESPN scoreboard API.

    Args:
        date (str): date to query in %Y%m%d format
        group (str): ESPN group to query

    Returns:
        dict: json response from the API
    """
    return ESPNAPI.query_scoreboard(date, group)


def query_team(team_id: str) -> dict:
    """Query the ESPN team API.

    Args:
        team_id (str): ESPN team ID

    Returns:
        dict: json response from the API
    """
    return ESPNAPI.query_team(team_id)


def query_game(game_id: str) -> dict:
    """Query the ESPN game API.

    Args:
        game_id (str): ESPN game ID

    Returns:
        dict: json response from the API
    """
    return ESPNAPI.query_game(game_id)
