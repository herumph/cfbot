"""SQLite models."""

from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Defintion of base model."""

    pass


class Post(Base):
    """Table definition for Post."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str] = mapped_column(String(80))
    cid: Mapped[str] = mapped_column(String(80))
    post_text: Mapped[str] = mapped_column(String(300))
    created_at_ts: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    updated_at_ts: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    root_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer)


class Game(Base):
    """Table definition for Game."""

    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    start_ts: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    home_team: Mapped[str] = mapped_column(String(50))
    away_team: Mapped[str] = mapped_column(String(50))
    home_team_id: Mapped[str] = mapped_column(String(20))
    away_team_id: Mapped[str] = mapped_column(String(20))
    home_wins: Mapped[int] = mapped_column(Integer)
    home_losses: Mapped[int] = mapped_column(Integer)
    home_conf_wins: Mapped[int] = mapped_column(Integer)
    home_conf_losses: Mapped[int] = mapped_column(Integer)
    away_wins: Mapped[int] = mapped_column(Integer)
    away_losses: Mapped[int] = mapped_column(Integer)
    away_conf_wins: Mapped[int] = mapped_column(Integer)
    away_conf_losses: Mapped[int] = mapped_column(Integer)
    home_score: Mapped[int] = mapped_column(Integer)
    away_score: Mapped[int] = mapped_column(Integer)
    networks: Mapped[str] = mapped_column(String(50))
    trackable: Mapped[bool] = mapped_column(Boolean)
    last_post_id: Mapped[Optional[int]] = mapped_column(Integer)
    end_ts: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP)


class Credentials(Base):
    """Table definition for Credentials."""

    __tablename__ = "credentials"

    username: Mapped[str] = mapped_column(String(80), primary_key=True)
    password: Mapped[str] = mapped_column(String(80))
    session: Mapped[str] = mapped_column(String(1000))
    type: Mapped[str] = mapped_column(String(50))


class Query(Base):
    """Table definition for ApiQueries."""

    __tablename__ = "api_queries"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    url: Mapped[str] = mapped_column(String(120))
    date_ts: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
