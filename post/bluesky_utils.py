import getpass

from atproto import Client
from atproto.exceptions import AtProtocolError, NetworkError

from db.db_utils import (
    insert_rows,
    update_rows,
    get_values,
    log_post_to_db,
    get_previous_posts,
)
from post.get_reply_ids import get_reply_ids
from post import CLIENT


def get_session(
    client: Client,
    username: str,
    refresh_session: bool | None = False,
) -> str:
    """Get session text files if they exist, otherwise prompt for username and
    password.

    Args:
        client (Client): atproto client
        username (str): bluesky username
        refresh_session (bool): bool to refresh the client session string

    Returns:
        session text information if it exists
    """
    credentials = get_values("credentials", {"username": username}, "first")
    session_string = credentials.session if credentials else None

    if not session_string:
        password = getpass.getpass("password:")
        client.login(username, password)
        session_string = client.export_session_string()
        insert_rows(
            "credentials",
            [{"username": username, "password": password, "session": session_string}],
        )

    elif refresh_session:
        client.login(credentials.username, credentials.password)
        session_string = client.export_session_string()
        update_rows(
            "credentials",
            {
                "username": credentials.username,
                "password": credentials.password,
                "session": session_string,
            },
            {"username": credentials.username},
        )

    return session_string


def init_client(username: str) -> Client:
    """Connect to bluesky using saved credentials.

    Args:
        username (str): username to connect with or save to the database

    Returns:
        Client: bluesky client
    """
    client = Client()
    session_string = get_session(client, username)

    # handle session string expiry and network issues
    try:
        client.login(session_string=session_string)
    except (AtProtocolError, NetworkError):
        client = Client()
        session_string = get_session(client, username, refresh_session=True)
        client.login(session_string=session_string)

    return client


def create_post(
    post_text,
    post_type,
    last_post_id: int | None = None,
) -> None:
    """Create a post that is either new or a reply to an existing post.

    Args:
        post_text (str): post text
        reply_ids (optional, dict): reply parameters of the parent and root posts
    """
    assert post_type in ("game_header", "game_update"), (
        "Invalid post type. Valid post taypes are 'game_header' and 'game_update'."
    )
    assert last_post_id is not None if post_type == "game_update" else True, (
        "last_post_id must be an integer or None."
    )

    post_params = {"text": post_text}
    bsky_ids = None
    if post_type == "game_update":
        previous_post = get_previous_posts(last_post_id)
        bsky_ids = get_reply_ids(previous_post)
        post_params["reply_to"] = bsky_ids

    post = CLIENT.send_post(**post_params)

    log_post_to_db(post.uri, post.cid, post_params, post_type, bsky_ids)
