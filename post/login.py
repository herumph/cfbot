"""Login to bluesky."""

import getpass

from atproto import Client
from atproto.exceptions import AtProtocolError, NetworkError
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from db.models import Credentials


def get_session(client: Client, db_session: Session, username: str, login_type: str, refresh_session: bool | None = False) -> str:
    """Get session text files if they exist, otherwise prompt for username and
    password.

    Args:
        client (Client): atproto client
        db_session (Session): credential database
        username (str): bluesky username
        login_type (str): type of login, prod or dev.
        refresh_session (bool): bool to refresh the client session string

    Returns:
        session text information if it exists
    """
    query = select(Credentials).filter(Credentials.username == username)
    credentials = db_session.execute(query).first()
    session_string = credentials[0].session if credentials else None

    if not session_string:
        password = getpass.getpass("password:")
        client.login(username, password)
        session_string = client.export_session_string()
        save_session(db_session, username, password, session_string, login_type)

    elif refresh_session:
        client.login(credentials[0].username, credentials[0].password)
        session_string = client.export_session_string()
        update_creds(db_session, credentials[0].username, session_string)

    return session_string


def save_session(db_session: Session, username: str, password: str, session_string: str, login_type: str):
    """Export current session to a text file.

    Args:
        db_session (Session): credential database
        username (str): username to save
        password (str): password to save
        session_string (str): session information
        login_type (str): type of login to save, prod or dev
    """
    query = insert(Credentials).values(
        {
            "username": username,
            "password": password,
            "session": session_string,
            "type": login_type,
        }
    )
    db_session.execute(query)
    db_session.commit()


def update_creds(db_session: Session, username: str, session_string: str):
    """Export current session to a text file.

    Args:
        username (str): username to update
        session_string (str): session information
        db_session (Session): database to update credentials
    """
    query = (
        update(Credentials)
        .where(Credentials.username == username)
        .values(
            {
                "session": session_string,
            }
        )
    )
    db_session.execute(query)
    db_session.commit()


def init_client(db_session: Session, username: str, login_type: str) -> Client:
    """Connect to bluesky using saved credentials.

    Args:
        db_session (Session): database to save credentials to
        username (str): username to connect with or save to the database
        login_type (str): type of login to save, prod or dev. Defaults to dev.

    Returns:
        Client: bluesky client
    """
    client = Client()
    session_string = get_session(client, db_session, username, login_type)

    # handle session string expiry and network issues
    try:
        client.login(session_string=session_string)
    except (AtProtocolError, NetworkError):
        client = Client()
        session_string = get_session(client, db_session, username, login_type, refresh_session=True)
        client.login(session_string=session_string)

    return client
