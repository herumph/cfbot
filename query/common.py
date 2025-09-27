"""ESPN API functions."""
import requests
from db.db_utils import save_api_query

ESPN_GAME = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event="
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="
ESPN_TEAM = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"


def call_espn(url: str) -> dict:
    """Query ESPN API.

    Args:
        url (str): url in espn's api to query

    Returns:
        dict: json response from the api
    """
    response = requests.get(url, timeout=10)
    save_api_query(url, response.status_code)

    if response.status_code == 200:
        return response.json()
    return None
