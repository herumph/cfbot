from typing import Optional

from atproto_client import Client, Session, SessionEvent


def get_session() -> Optional[str]:
    try:
        with open("session.txt") as f:
            return f.read()
    except FileNotFoundError:
        return None


def save_session(session_string: str) -> None:
    with open("session.txt", "w") as f:
        f.write(session_string)


def on_session_change(event: SessionEvent, session: Session) -> None:
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        save_session(session.export())


def init_client() -> Client:
    client = Client()
    client.on_session_change(on_session_change)

    session_string = get_session()
    client.login(session_string=session_string)

    return client
