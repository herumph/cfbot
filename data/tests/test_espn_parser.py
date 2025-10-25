import pytest
from data.espn_parser import ESPNParser


class TestESPNParser:
    def test_get_scoring_plays_missed_pat(self, game_with_missed_pat):
        plays = ESPNParser.scoring_plays(game_with_missed_pat)

        assert len(plays) == 9

        assert plays[0]["home_score"] == 7
        assert plays[0]["away_score"] == 0
        assert plays[0]["total_score"] == 7
        assert plays[0]["drive_description"] == None
        assert (
            plays[0]["play_text"]
            == "Jackson Arnold 1 Yd Run (Tyler Keltner Kick)"
        )
        assert plays[0]["scoring_team"] == "201"

        assert plays[3]["home_score"] == 21
        assert plays[3]["away_score"] == 6
        assert plays[3]["total_score"] == 27
        assert plays[3]["drive_description"] == None
        assert (
            plays[3]["play_text"]
            == "Reggie Brown 7 Yd pass from Ty Thompson (Ethan Head PAT failed)"
        )
        assert plays[3]["scoring_team"] == "2655"

    def test_get_scoring_plays_pick_six(self, game_with_pick_six):
        plays = ESPNParser.scoring_plays(game_with_pick_six)

        assert len(plays) == 2

        assert plays[1]["home_score"] == 14
        assert plays[1]["away_score"] == 0
        assert plays[1]["total_score"] == 14
        assert plays[1]["drive_description"] == None
        assert (
            plays[1]["play_text"]
            == "A. Swann pass intercepted,A. McCoy return for 26 yds for a TD (C. Boomer KICK)"
        )
        assert plays[1]["scoring_team"] == "68"

    @pytest.mark.skip(reason="not currently supported")
    def test_get_scoring_plays_safety(self, game_with_safety): ...

    def test_parse_games(self, scoreboard):
        games = ESPNParser.games(scoreboard)
        assert len(games) == 3

        assert games[0]["id"] == "401754543"
        assert games[0]["start_ts"].strftime("%Y-%m-%d %H:%M") == "2025-09-26 23:00"
        assert games[0]["networks"] == "ESPN"
        assert games[0]["home_score"] == 0
        assert games[0]["away_score"] == 0
        assert games[0]["trackable"] is True

    def test_parse_team_records(self, scoreboard):
        for event in scoreboard["events"]:
            competitors = ESPNParser.competitors(
                event["competitions"][0]["competitors"]
            )

        assert competitors["home_wins"] == "0"
        assert competitors["home_losses"] == "5"
        assert competitors["home_conf_wins"] == "0"
        assert competitors["home_conf_losses"] == "0"

        assert competitors["away_wins"] == "4"
        assert competitors["away_losses"] == "0"
        assert competitors["away_conf_wins"] == "1"
        assert competitors["away_conf_losses"] == "0"

    def test_parse_competitors(self, scoreboard):
        for event in scoreboard["events"]:
            competitors = ESPNParser.competitors(
                event["competitions"][0]["competitors"]
            )

        assert competitors["home_team_id"] == "204"
        assert competitors["home_team"] == "Oregon St"
        assert competitors["away_team_id"] == "248"
        assert competitors["away_team"] == "Houston"

    def test_team_streak_losing(self, losing_team):
        streak = ESPNParser.team_streak(losing_team)

        assert streak == "L4"

    def test_team_streak_winning(self, winning_team):
        streak = ESPNParser.team_streak(winning_team)

        assert streak == "W8"
