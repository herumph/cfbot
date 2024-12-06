import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from create_db import init_db_session
from login import init_client
from create_post import create_post


# needed connections
session = init_db_session()
client = init_client()

reply_ids = None
for _ in range(0, 3):
    post_id = create_post(client, session, post_text="test post", reply_ids=reply_ids)
    reply_ids = {"root": 1, "parent": post_id}