from datetime import datetime, timedelta
from time import sleep  # TODO: delete this for cron setup

from sqlalchemy import select
from sqlalchemy.orm import Session

from create_db import init_db_session
from models import Game
from post_game_headers import post_about_current_games
from post_important_plays import post_about_game


def get_active_games(session: Session, start_date: datetime) -> list[Game]:
    query = select(Game).filter((Game.start_ts <= start_date), (Game.end_ts == None))
    rows = session.execute(query)

    return [row[0] for row in rows]


if __name__ == "__main__":
    while True:
        # first run `get_games.py` for the day
        session = init_db_session()
        date = datetime.utcnow()

        # create root game post
        post_about_current_games(date)

        games = get_active_games(session, date)
        for game in games:
            print(date, game.id, game.home_team, game.away_team)
            post_about_game(game.id, datetime.utcnow() - timedelta(minutes=5))

        sleep(60)
