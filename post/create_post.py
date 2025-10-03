"""Create post on bluesky and log its information to appropriate tables."""

from datetime import datetime, timezone
from typing import Optional

from atproto_client.models.app.bsky.feed.post import CreateRecordResponse
from common import CLIENT, DB_SESSION
from sqlalchemy import select

from db.models import Post


def _query_for_post_ids(reply_ids: dict[str, str], key: str) -> dict:
    """Gather information for a parent/root post from the sqlite database.

    Args:
        reply_ids (dict): dictionary containing the post id of the parent and/or root post
        key (str): dictionary key that contains the post id to query

    Returns:
        dict: containing 'uri' and 'cid' for the queried post
    """
    query = select(Post).filter(Post.id == reply_ids[key])
    post = DB_SESSION.execute(query).first()
    assert post, f"No post for id: {reply_ids[key]} found"

    return {"uri": post[0].uri, "cid": post[0].cid}


def _get_reply_ids(reply_ids: dict[str, dict]) -> dict:
    """Gather information for the parent and root posts from the sqlite
    database.

    Args:
        reply_ids (dict): dictionary containing the post id of the parent and/or root post

    Returns:
        dict: containing 'parent' and 'root' post information for the queried post
    """
    assert "parent" in reply_ids.keys() and "root" in reply_ids.keys(), (
        "both parent and root ids must be included for a reply"
    )

    parent = _query_for_post_ids(DB_SESSION, reply_ids, "parent")
    if reply_ids["parent"] == reply_ids["root"] or reply_ids["root"] is None:
        return {"parent": parent, "root": parent}
    root = _query_for_post_ids(DB_SESSION, reply_ids, "root")

    return {"parent": parent, "root": root}


def _log_post_to_db(
    post: CreateRecordResponse,
    post_params: dict[str, str],
    post_type: str,
    reply_ids: dict[str, dict],
) -> str:
    """Logs created post to the Post table.

    Args:
        post (CreateRecordResponse): bluesky response after post creation
        post_params (dict): parameters of the post including ids and post text
        reply_ids (dict): ids of the parent and root posts

    Returns:
        str: post id of the newly created database entry
    """
    new_post = Post(
        uri=post.uri,
        cid=post.cid,
        post_text=post_params["text"],
        created_at_ts=datetime.now(timezone.utc),
        updated_at_ts=datetime.now(timezone.utc),
        post_type=post_type,
    )

    if reply_ids:
        new_post.root_id = reply_ids["root"]
        new_post.parent_id = reply_ids["parent"]

    DB_SESSION.add(new_post)
    DB_SESSION.commit()

    return new_post.id


def create_post(
    post_text,
    post_type,
    reply_ids: Optional[dict[str, int]] = None,
) -> str:
    """Create a post that is either new or a reply to an existing post.

    Args:
        post_text (str): post text
        reply_ids (optional, dict): reply parameters of the parent and root posts

    Returns:
        str: post id of the newly created database entry
    """
    post_params = {}
    if reply_ids:
        bsky_ids = _get_reply_ids(reply_ids)
        post_params["reply_to"] = bsky_ids

    post_params["text"] = post_text
    post = CLIENT.send_post(**post_params)

    return _log_post_to_db(post, post_params, post_type, reply_ids)
