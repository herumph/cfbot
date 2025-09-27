import logging
from datetime import datetime

import requests

from db.db_utils import add_record


class _ESPNAPI():
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

    def _call_espn(self, url: str) -> dict:
        """Query ESPN API.

        Args:
            url (str): url in espn's api to query

        Returns:
            dict: json response from the api
        """
        response = requests.get(url, timeout=10)
        add_record("api_queries", {"url": url, "status_code": response.status_code, "date_ts": datetime.now()})

        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error querying ESPN API: {response.status_code} for URL {url}")
            return {}

    def _create_scoreboard_url(self, date: str, group: str) -> str:
        """Generate a scoreboard query URL.

        Args:
            date (str): date to query in %Y%m%d format
            group (str): ESPN group to query

        Returns:
            str: full URL to query the ESPN scoreboard API
        """
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise AssertionError("Date must be in %Y%m%d format")
        assert len(group), "Group must be a non-empty string"

        return f"{self.scoreboard}{date}&groups={group}"

    def _create_team_url(self, team_id: str) -> str:
        """Generate a team query URL.

        Args:
            team_id (str): ESPN team ID

        Returns:
            str: full URL to query the ESPN team API
        """
        assert len(team_id), "team_id must be a non-empty string"
        
        return f"{self.team}{team_id}"

    def _create_game_url(self, game_id: str) -> str:
        """Generate a game query URL.

        Args:
            game_id (str): ESPN game ID

        Returns:
            str: full URL to query the ESPN game API
        """
        assert len(game_id), "game_id must be a non-empty string"

        return f"{self.game}{game_id}"

    def query_scoreboard(self, date: str, group: str) -> dict:
        """Query the ESPN scoreboard API.

        Args:
            date (str): date to query in %Y%m%d format
            group (str): ESPN group to query

        Returns:
            dict: json response from the API
        """
        return self._call_espn(self._create_scoreboard_url(date, group))

    def query_team(self, team_id: str) -> dict:
        """Query the ESPN team API.

        Args:
            team_id (str): ESPN team ID

        Returns:
            dict: json response from the API
        """
        return self._call_espn(self._create_team_url(team_id))

    def query_game(self, game_id: str) -> dict:
        """Query the ESPN game API.

        Args:
            game_id (str): ESPN game ID

        Returns:
            dict: json response from the API
        """
        return self._call_espn(self._create_game_url(game_id))


ESPNAPI = _ESPNAPI()
