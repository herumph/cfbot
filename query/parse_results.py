from query.espn_parser import ESPNParser


def parse_games(game_json: dict) -> list[dict]:
    """Parse game information from an ESPN scoreboard response.

    Args:
        game_json (dict): ESPN API response from the ESPN scoreboard for a given league

    Returns:
        list[dict]: list of games to be added to the SQLite database
    """
    return ESPNParser.parse_games(game_json)


def get_scoring_plays(game_json: dict) -> list[dict[str, str]]:
    """Gets scoring plays from an ESPN API response and returns them sorted by
    time.

    Args:
        game_json (dict): ESPN API response
    Returns:
        list[dict]: list containing all scoring plays from the game that haven't been posted about yet
    """
    return ESPNParser.get_scoring_plays(game_json)