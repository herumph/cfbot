import getpass

from atproto import Client
from atproto.exceptions import AtProtocolError, NetworkError

from post import BSKY_USERNAME
from db.db_utils import (
    insert_rows,
    update_rows,
    get_values,
)


class _BlueSky:
    def __init__(self, username: str) -> None:
        self.username = username
        self._init_client()

    def _get_session(
        self,
        client: Client,
        refresh_session: bool | None = False,
    ) -> str:
        """Get session text files if they exist, otherwise prompt for username and
        password.

        Args:
            client (Client): atproto client
            refresh_session (bool): bool to refresh the client session string

        Returns:
            session text information if it exists
        """
        credentials = get_values("credentials", {"username": self.username}, "first")
        session_string = credentials.session if credentials else None

        if not session_string:
            password = getpass.getpass("password:")
            client.login(self.username, password)
            session_string = client.export_session_string()
            insert_rows(
                "credentials",
                [
                    {
                        "username": self.username,
                        "password": password,
                        "session": session_string,
                    }
                ],
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

    def _init_client(self):
        """Connect to bluesky using saved credentials."""
        session_string = self._get_session(self.client)

        # handle session string expiry and network issues
        try:
            self.client.login(session_string=session_string)
        except (AtProtocolError, NetworkError):
            self.client = Client()
            session_string = self._get_session(self.client, refresh_session=True)
            self.client.login(session_string=session_string)

    def create_post(
        self,
        post_params,
    ) -> object:
        """Create a post that is either new or a reply to an existing post."""
        return self.client.send_post(**post_params)


Bluesky = _BlueSky(username=BSKY_USERNAME)
