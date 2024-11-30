from datetime import datetime, timezone
from typing import Optional

from atproto_client import Client
from atproto_client.models.app.bsky.feed.post import CreateRecordResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Post


def _query_for_post_ids(session: Session, reply_ids: dict, key: str) -> dict:
    # get parent post information
    query = select(Post).filter(Post.id == reply_ids[key])
    post = session.execute(query).first()
    assert post, f"No post for id: {reply_ids[key]} found"

    return {"uri": post[0].uri, "cid": post[0].cid}


def _get_reply_ids(session: Session, reply_ids: dict) -> dict:
    assert "parent" in reply_ids.keys() and "root" in reply_ids.keys(), "both parent and root ids must be included for a reply"

    parent = _query_for_post_ids(session, reply_ids, "parent")
    if reply_ids["parent"] == reply_ids["root"] or reply_ids["root"] is None:
        return {"parent": parent, "root": parent}
    root = _query_for_post_ids(session, reply_ids, "root")

    return {"parent": parent, "root": root}


def log_post_to_db(session: Session, post: CreateRecordResponse, post_params: dict, reply_ids: dict) -> str:
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
    reply_ids: Optional[dict[str, str]] = None,
) -> CreateRecordResponse:
    """
    Create a post that is either new or a reply to an existing post

    Args:
        client (Client): connection to bluesky
        post_text (str): post text
        is_reply (optional, bool): if the post being made is a reply
        reply_ids (optional, dict): reply parameters of the parent and root posts

    Returns:
        CreateRecordResponse containing the uri and cid of the post that was created
    """
    post_params = {}
    if reply_ids:
        bsky_ids = _get_reply_ids(session, reply_ids)
        post_params["reply_to"] = bsky_ids

    post_params["text"] = post_text
    post = client.send_post(**post_params)

    return log_post_to_db(session, post, post_params, reply_ids)
