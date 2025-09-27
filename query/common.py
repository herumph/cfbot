"""ESPN API functions."""
import logging

import requests

from db.db_utils import add_record


class ESPNAPI:
    """ESPN API endpoints."""

    @property
    def game(self) -> str:
        return "https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event="

    @property
    def scoreboard(self) -> str:
        return "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="

    @property
    def team(self) -> str:
        return "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"
    

ESPNAPIUrls = ESPNAPI()


def _call_espn(url: str) -> dict:
    """Query ESPN API.

    Args:
        url (str): url in espn's api to query

    Returns:
        dict: json response from the api
    """
    response = requests.get(url, timeout=10)
    add_record("api_queries", url, response.status_code)

    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error querying ESPN API: {response.status_code} for URL {url}")
        return None


def _create_scoreboard_url(date: str, group: str) -> str:
    """Generate a scoreboard query URL.

    Args:
        date (str): date to query in %Y%m%d format
        group (str): ESPN group to query

    Returns:
        str: full URL to query the ESPN scoreboard API
    """
    return f"{ESPNAPIUrls.scoreboard}{date}&groups={group}"
    

def _create_team_url(team_id: str) -> str:
    """Generate a team query URL.

    Args:
        team_id (str): ESPN team ID

    Returns:
        str: full URL to query the ESPN team API
    """
    return f"{ESPNAPIUrls.team}{team_id}"


def _create_game_url(game_id: str) -> str:
    """Generate a game query URL.

    Args:
        game_id (str): ESPN game ID

    Returns:
        str: full URL to query the ESPN game API
    """
    return f"{ESPNAPIUrls.game}{game_id}"


def query_scoreboard(date: str, group: str) -> dict:
    """Query the ESPN scoreboard API.

    Args:
        date (str): date to query in %Y%m%d format
        group (str): ESPN group to query

    Returns:
        dict: json response from the API
    """
    return _call_espn(_create_scoreboard_url(date, group))


def query_team(team_id: str) -> dict:
    """Query the ESPN team API.

    Args:
        team_id (str): ESPN team ID

    Returns:
        dict: json response from the API
    """
    return _call_espn(_create_team_url(team_id))


def query_game(game_id: str) -> dict:
    """Query the ESPN game API.

    Args:
        game_id (str): ESPN game ID

    Returns:
        dict: json response from the API
    """
    return _call_espn(_create_game_url(game_id))