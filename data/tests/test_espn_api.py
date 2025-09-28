import pytest
from data.espn_api import ESPNAPI


class TestESPNAPI:
    def test_create_team_url(self):
        team_id = "123"
        expected_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}"
        assert ESPNAPI._create_team_url(team_id) == expected_url

    def test_create_team_url_invalid(self):
        team_id = ""
        with pytest.raises(AssertionError):
            ESPNAPI._create_team_url(team_id)

    def test_create_game_url(self):
        game_id = "456"
        expected_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
        assert ESPNAPI._create_game_url(game_id) == expected_url

    def test_create_game_url_invalid(self):
        game_id = ""
        with pytest.raises(AssertionError):
            ESPNAPI._create_game_url(game_id)

    def test_create_scoreboard_url(self):
        date = "20240101"
        group = "80"
        expected_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={date}&groups={group}"
        assert ESPNAPI._create_scoreboard_url(date, group) == expected_url

    def test_create_scoreboard_url_invalid_date(self):
        date = ""
        group = "80"
        with pytest.raises(AssertionError):
            ESPNAPI._create_scoreboard_url(date, group)

    def test_create_scoreboard_url_invalid_group(self):
        date = "20240101"
        group = ""
        with pytest.raises(AssertionError):
            ESPNAPI._create_scoreboard_url(date, group)
