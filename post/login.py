"""Login to bluesky."""

import getpass
from typing import Optional

from atproto import Client
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.create_db import init_db_session
from db.models import Credentials


def get_session(client: Client, db_session: Session, login_type: str | None = None) -> Optional[str]:
    """Get session text files if they exist, otherwise prompt for username and
    password.

    Returns:
        session text information if it exists
    """
    query = select(Credentials).filter(Credentials.type == login_type)
    credentials = db_session.execute(query).first()
    
    if not credentials:
        user = getpass.getpass("user:")
        password = getpass.getpass("password:")
        client.login(user, password)
        session_string = client.export_session_string()

        save_session(session_string)
    return session_string


def save_session(session_string: str):
    """Export current session to a text file.

    Args:
        session_string (str): session information
    """
    with open("session.txt", "w") as f:
        f.write(session_string)


def init_client(db_session: Session) -> Client:
    """Connect to bluesky using saved credentials.

    Returns:
        Client: bluesky client
    """
    client = Client()
    # client.on_session_change(on_session_change)

    session_string = get_session(client, db_session)
    client.login(session_string=session_string)

    return client


if __name__ == "__main__":
    init_client(init_db_session())