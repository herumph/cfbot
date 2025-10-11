from typing import Any

from db.db_utils import get_values


def query_for_post_ids(reply_ids: dict[str, str], key: str) -> dict:
    """Gather information for a parent/root post from the sqlite database.

    Args:
        reply_ids (dict): dictionary containing the post id of the parent and/or root post
        key (str): dictionary key that contains the post id to query

    Returns:
        dict: containing 'uri' and 'cid' for the queried post
    """
    post = get_values("posts", {"id": reply_ids[key]}, "first")

    return {"uri": post.uri, "cid": post.cid}


def get_reply_ids(reply_ids: dict[str, Any]) -> dict:
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

    parent = query_for_post_ids(reply_ids, "parent")
    if reply_ids["parent"] == reply_ids["root"] or reply_ids["root"] is None:
        return {"parent": parent, "root": parent}
    root = query_for_post_ids(reply_ids, "root")

    return {"parent": parent, "root": root}
