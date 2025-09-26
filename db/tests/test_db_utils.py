import logging
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db.create_db import init_db_session
from db.db_utils import get_a_days_games, insert_rows
from db.models import Game

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

    def test_get_a_days_games_no_games(self):
        games = get_a_days_games(datetime(1700, 1, 1))
        assert logging.getLogger().level == logging.WARNING
        assert games == []

    def test_get_a_days_games_with_games(self):
        self.session.add(self.valid_game)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

        games = get_a_days_games(self.valid_game.start_ts)
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
        insert_rows(Game, [self.valid_game])

        statement = select(Game).filter(Game.id == self.valid_game["id"])
        rows = self.session.execute(statement).all()
        
        assert len(rows) == 1
        assert int(rows[0].Game.id) == self.valid_game["id"]
        assert rows[0].Game.home_team == self.valid_game["home_team"]
        assert rows[0].Game.away_team == self.valid_game["away_team"]