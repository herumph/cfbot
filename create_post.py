"""
Create post on bluesky and log its information to appropriate tables
"""

from datetime import datetime, timezone
from typing import Optional

from atproto_client import Client
from atproto_client.models.app.bsky.feed.post import CreateRecordResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Post


def _query_for_post_ids(session: Session, reply_ids: dict[str, str], key: str) -> dict:
    """
    Gather information for a parent/root post from the sqlite database

    Args:
        session (Session): SQLite session
        reply_ids (dict): dictionary containing the post id of the parent and/or root post
        key (str): dictionary key that contains the post id to query

    Returns:
        dict: containing 'uri' and 'cid' for the queried post
    """
    query = select(Post).filter(Post.id == reply_ids[key])
    post = session.execute(query).first()
    assert post, f"No post for id: {reply_ids[key]} found"

    return {"uri": post[0].uri, "cid": post[0].cid}


def _get_reply_ids(session: Session, reply_ids: dict[str, dict]) -> dict:
    """
    Gather information for the parent and root posts from the sqlite database

    Args:
        session (Session): SQLite session
        reply_ids (dict): dictionary containing the post id of the parent and/or root post

    Returns:
        dict: containing 'parent' and 'root' post information for the queried post
    """
    assert "parent" in reply_ids.keys() and "root" in reply_ids.keys(), "both parent and root ids must be included for a reply"

    parent = _query_for_post_ids(session, reply_ids, "parent")
    if reply_ids["parent"] == reply_ids["root"] or reply_ids["root"] is None:
        return {"parent": parent, "root": parent}
    root = _query_for_post_ids(session, reply_ids, "root")

    return {"parent": parent, "root": root}


def log_post_to_db(session: Session, post: CreateRecordResponse, post_params: dict[str, str], reply_ids: dict[str, dict]) -> str:
    """
    Logs created post to the Post table

    Args:
        session (Session): SQLite session
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
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    if reply_ids:
        new_post.root_id = reply_ids["root"]
        new_post.parent_id = reply_ids["parent"]

    session.add(new_post)
    session.commit()

    return new_post.id


def create_post(
    client: Client,
    session: Session,
    post_text,
    reply_ids: Optional[dict[str, int]] = None,
) -> str:
    """
    Create a post that is either new or a reply to an existing post

    Args:
        client (Client): connection to bluesky
        post_text (str): post text
        reply_ids (optional, dict): reply parameters of the parent and root posts

    Returns:
        str: post id of the newly created database entry
    """
    post_params = {}
    if reply_ids:
        bsky_ids = _get_reply_ids(session, reply_ids)
        post_params["reply_to"] = bsky_ids

    post_params["text"] = post_text
    post = client.send_post(**post_params)

    return log_post_to_db(session, post, post_params, reply_ids)
