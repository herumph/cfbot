from db.db_utils import get_values, log_post_to_db
from post import CLIENT


# TODO: add test, move to db_utils
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


# TODO: add test, move to db_utils
def get_reply_ids(reply_ids: dict[str, dict]) -> dict:
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


# TODO: move to a bluesky_utils file
def create_post(
    post_text,
    post_type,
    reply_ids: dict | None = None,
) -> int:
    """Create a post that is either new or a reply to an existing post.

    Args:
        post_text (str): post text
        reply_ids (optional, dict): reply parameters of the parent and root posts

    Returns:
        str: post id of the newly created database entry
    """
    post_params = {}
    if reply_ids:
        bsky_ids = get_reply_ids(reply_ids)
        post_params["reply_to"] = bsky_ids

    post_params["text"] = post_text
    post = CLIENT.send_post(**post_params)

    return log_post_to_db(post.uri, post.cid, post_params, post_type, reply_ids)
