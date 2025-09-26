"""ESPN API functions."""
from datetime import datetime, timezone

import requests

from common import DB_SESSION
from db.models import Query

ESPN_GAME = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event="
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="
ESPN_TEAM = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"


def save_api_query(url: str, status_code: int):
    """Saves a query to the database.

    Args:
        url (str): url that was queried
        status_code (int): status code of the api response
    """
    query = Query(url=url, status_code=status_code, date_ts=datetime.now(timezone.utc))
    DB_SESSION.add(query)
    DB_SESSION.commit()


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
