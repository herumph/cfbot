from datetime import datetime


class _ESPNParser:
    """Class to parse ESPN API responses."""

    def team_records(
        self, teams: dict[str, str], home_away: str, records: list[dict]
    ) -> dict[str, str]:
        """Parse record information from an ESPN API response.

        Args:
            teams (dict): dictionary containing information about home and away teams
            home_away (str): string whose value is either 'home' or 'away'
            records (list[dict]): list of record information from the ESPN API

        Returns:
            teams dictionary with total records and conference records populated.
        """
        assert home_away in ("home", "away"), (
            "home_away variable must be either home or away."
        )

        for record in records:
            if record["type"] == "total":
                teams[f"{home_away}_wins"], teams[f"{home_away}_losses"] = record[
                    "summary"
                ].split("-")
            elif record["type"] == "vsconf":
                teams[f"{home_away}_conf_wins"], teams[f"{home_away}_conf_losses"] = (
                    record["summary"].split("-")
                )

        return teams

    def competitors(self, competitors: list[dict]) -> dict[str, str]:
        """Gather competitor information from an ESPN API response.

        Args:
            competitiors (list[dict]): list containing all teams involved in a competition

        Returns:
            dictionary containing home and away team names and records
        """
        teams = {}
        for team in competitors:
            teams[f"{team['homeAway']}_team"] = team["team"]["shortDisplayName"]
            teams[f"{team['homeAway']}_team_id"] = team["id"]
            teams = self.team_records(teams, team["homeAway"], team["records"])

        return teams

    def games(self, game_json: dict) -> list[dict]:
        """Parse game information from the ESPN scoreboard.

        Args:
            game_json (dict): ESPN API response from the ESPN scoreboard for a given league

        Returns:
            list[dict]: list of games to be added to the database
        """
        games = []
        for event in game_json["events"]:
            competitors = self.competitors(event["competitions"][0]["competitors"])
            games.append(
                {
                    "id": event["id"],
                    "start_ts": datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ"),
                    "networks": event["competitions"][0]["broadcast"],
                    "home_score": 0,
                    "away_score": 0,
                    "trackable": True,
                    **competitors,
                }
            )

        return games

    def scoring_plays(self, game_json: dict) -> list[dict[str, str]]:
        """Gets scoring plays from an ESPN API response and returns them sorted
        by time.

        Args:
            game_json (dict): ESPN API response

        Returns:
            list[dict]: list containing all scoring plays from the game that haven't been posted about yet
        """
        results = []
        if "drives" not in game_json.keys():
            return results
        if "previous" not in game_json["drives"].keys():
            return results

        is_complete = game_json["header"]["competitions"][0]["status"]["type"][
            "completed"
        ]
        all_drives = game_json["drives"]["previous"]
        for drive in all_drives:
            scoring_plays = [play for play in drive["plays"] if play["scoringPlay"]]
            for ind, play in enumerate(
                scoring_plays
            ):  # yes, there can be multiple scoring plays in one drive according to ESPN
                if drive["isScore"]:
                    drive_description = drive["description"] if ind == 0 else None
                    results.append(
                        {
                            "game_id": game_json["header"]["id"],
                            "play_text": play["text"],
                            "away_score": play["awayScore"],
                            "home_score": play["homeScore"],
                            "total_score": play["homeScore"]
                            + play[
                                "awayScore"
                            ],  # needed because ESPN doesn't know how clocks work
                            "drive_description": drive_description,
                            "scoring_team": play["end"]["team"]["id"],
                            "is_complete": is_complete,
                        }
                    )

        return sorted(results, key=lambda d: d["total_score"])

    # TODO: add tests
    def team_streak(self, team_info: dict) -> str:
        """Gather win/loss streaks from ESPN API json.

        Args:
            team_info (dict): ESPN API json response

        Returns:
            string: formatted win/loss streak
        """
        streak = [
            stat["value"]
            for stat in team_info["team"]["record"]["items"][0]["stats"]
            if stat["name"] == "streak"
        ][0]
        streak = f"W{streak}" if streak >= 0 else f"L{str(streak).strip('-')}"
        return str(streak)[:-2]


ESPNParser = _ESPNParser()
