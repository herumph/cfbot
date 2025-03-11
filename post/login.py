"""Login to bluesky."""

import getpass
from typing import Optional

from atproto import Client
from atproto.exceptions import AtProtocolError, NetworkError
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from db.create_db import init_db_session
from db.models import Credentials


def get_session(client: Client, db_session: Session, login_type: str | None = "dev", refresh_session: bool | None = False) -> Optional[str]:
    """Get session text files if they exist, otherwise prompt for username and
    password.

    Returns:
        session text information if it exists
    """
    query = select(Credentials).filter(Credentials.type == login_type)
    credentials = db_session.execute(query).first()
    session_string = credentials[0].session if credentials else None

    if not session_string:
        user = getpass.getpass("user:")
        password = getpass.getpass("password:")
        client.login(user, password)
        session_string = client.export_session_string()
        save_session(user, password, session_string, db_session, login_type)

    elif refresh_session:
        client.login(credentials[0].username, credentials[0].password)
        session_string = client.export_session_string()
        update_creds(credentials[0].username, session_string, db_session)

    return session_string


def save_session(user: str, password: str, session_string: str, db_session: Session, login_type: str):
    """Export current session to a text file.

    Args:
        session_string (str): session information
    """
    query = insert(Credentials).values(
        {
            "username": user,
            "password": password,
            "session": session_string,
            "type": login_type,
        }
    )
    db_session.execute(query)
    db_session.commit()


def update_creds(user: str, session_string: str, db_session: Session):
    """Export current session to a text file.

    Args:
        session_string (str): session information
    """
    query = (
        update(Credentials)
        .where(Credentials.username == user)
        .values(
            {
                "session": session_string,
            }
        )
    )
    db_session.execute(query)
    db_session.commit()


def init_client(db_session: Session) -> Client:
    """Connect to bluesky using saved credentials.

    Returns:
        Client: bluesky client
    """
    client = Client()
    session_string = get_session(client, db_session)

    # handle session string expiry and network issues
    try:
        client.login(session_string=session_string)
    except (AtProtocolError, NetworkError):
        client = Client()
        session_string = get_session(client, db_session, refresh_session=True)
        client.login(session_string=session_string)

    return client


# TODO: remove this
if __name__ == "__main__":
    init_client(init_db_session())
