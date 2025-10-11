from datetime import datetime, timezone

from db.db_utils import (
    add_record,
    get_previous_posts,
)
from post.get_reply_ids import get_reply_ids
from post.bluesky import Bluesky


def get_post_params(
    post_text,
    post_type,
    last_post_id: int | None = None,
) -> dict:
    """Create a post that is either new or a reply to an existing post.

    Args:
        post_text (str): post text
        post_type (str): type of post, either 'game_header' or 'game_update'
        last_post_id (optional, int): ID of the last post for replies
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

    return post_params


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
    post_params = get_post_params(post_text, post_type, last_post_id)
    post = Bluesky.create_post(post_params)

    add_record(
        "posts",
        {
            "uri": post.uri,
            "cid": post.cid,
            "post_text": post_text,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "post_type": post_type,
            "root_id": post_params.get("root_id", None),
            "parent_id": post_params.get("parent_id", None),
        },
    )
