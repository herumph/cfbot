"""Login to bluesky."""

import getpass
from typing import Optional

from atproto import Client, Session, SessionEvent


def get_session(client: Client) -> Optional[str]:
    """Get session text files if they exist, otherwise prompt for username and
    password.

    Returns:
        session text information if it exists
    """
    try:
        with open("session.txt") as f:
            return f.read()
    except FileNotFoundError:
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


def on_session_change(event: SessionEvent, session: Session):
    """Export session if there is a change.

    Args:
        event (SessionEvent): session trigger event
        session (Sessions): bluesky session
    """
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        save_session(session.export())


def init_client() -> Client:
    """Connect to bluesky using saved credentials.

    Returns:
        Client: bluesky client
    """
    client = Client()
    client.on_session_change(on_session_change)

    session_string = get_session(client)
    client.login(session_string=session_string)

    return client
