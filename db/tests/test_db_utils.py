import logging
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.create_db import init_db_session
from db.db_utils import add_record, get_games, get_db_tables, insert_rows
from db.models import Game, Query

DB_SESSION = init_db_session()


class TestGetADaysGames:
    def setup_class(self):
        self.session = DB_SESSION
        self.valid_game = Game(
            id=-100,
            start_ts=datetime(1805, 1, 1),
            home_team="test_home_team",
            away_team="test_away_team",
            home_team_id="test_home_id",
            away_team_id="test_away_id",
            home_wins=1,
            home_losses=0,
            home_conf_wins=0,
            home_conf_losses=0,
            away_wins=0,
            away_losses=1,
            away_conf_wins=0,
            away_conf_losses=1,
            home_score=0,
            away_score=14,
            networks="",
            trackable=False,
        )

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_get_a_days_games_no_games(self, caplog):
        with caplog.at_level(logging.INFO):
            games = get_games(datetime(1700, 1, 1), datetime(1700, 1, 2))
        assert any("No games found for date" in message for message in caplog.messages)

    def test_get_a_days_games_with_games(self):
        self.session.add(self.valid_game)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

        games = get_games(
            self.valid_game.start_ts, self.valid_game.start_ts + timedelta(days=1)
        )
        self.teardown_class()

        assert len(games)
        assert int(games[0].id) == self.valid_game.id
        assert games[0].home_team == self.valid_game.home_team
        assert games[0].away_team == self.valid_game.away_team


class TestInsertRows:
    def setup_class(self):
        self.session = DB_SESSION
        self.valid_game = {
            "id": -8,
            "start_ts": datetime(1801, 1, 1),
            "home_team": "test_home_team",
            "away_team": "test_away_team",
            "home_team_id": "test_home_id",
            "away_team_id": "test_away_id",
            "home_wins": 1,
            "home_losses": 0,
            "home_conf_wins": 0,
            "home_conf_losses": 0,
            "away_wins": 0,
            "away_losses": 1,
            "away_conf_wins": 0,
            "away_conf_losses": 1,
            "home_score": 0,
            "away_score": 14,
            "networks": "",
            "trackable": False,
        }

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_insert_values_success(self):
        insert_rows("games", [self.valid_game])

        statement = select(Game).filter(Game.id == self.valid_game["id"])
        rows = self.session.execute(statement).all()

        assert len(rows) == 1
        assert int(rows[0].Game.id) == self.valid_game["id"]
        assert rows[0].Game.home_team == self.valid_game["home_team"]
        assert rows[0].Game.away_team == self.valid_game["away_team"]

    def test_insert_values_no_rows(self, caplog):
        with caplog.at_level(logging.INFO):
            insert_rows("games", [])
        assert any("No rows to insert" in message for message in caplog.messages)


class TestAddRecord:
    def setup_class(self):
        self.session = DB_SESSION
        self.valid_url = "https://example.com"
        self.valid_status_code = 200

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_save_api_query_success(self):
        add_record(
            "api_queries",
            {
                "url": self.valid_url,
                "status_code": self.valid_status_code,
                "date_ts": datetime.now(),
            },
        )

        statement = select(Query).filter(Query.url == self.valid_url)
        rows = self.session.execute(statement).all()

        assert rows[0].Query.url == self.valid_url
        assert rows[0].Query.status_code == self.valid_status_code

    def test_save_api_query_no_values(self, caplog):
        with caplog.at_level(logging.INFO):
            add_record("api_queries", {})
        assert any("No values to insert" in message for message in caplog.messages)


class TestGetDBTables:
    def setup_class(self):
        self.session = DB_SESSION

    def test_get_db_tables_existing_table(self):
        valid_table = "games"

        table = get_db_tables(valid_table)

        assert table
        assert table.__tablename__ == "games"

    def test_get_db_tables_invalid_table(self):
        invalid_table = "__not_a_real_table"

        with pytest.raises(ValueError) as excinfo:
                get_db_tables(invalid_table)
        assert "Table __not_a_real_table not found in database" in str(excinfo.value)