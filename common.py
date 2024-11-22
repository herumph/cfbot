import requests

ESPN_GAME = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event="
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="
ESPN_TEAM = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/"


def call_espn(url: str) -> dict:
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return None
